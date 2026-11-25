# Food Label Verification System — Compact Project Reference

> **Document Type:** Compact Technical Reference for Claude AI Report Review & Modification  
> **System Name:** Food Label Verification System  
> **Degree & Institution:** Master of Computer Applications (MCA), MITE, Moodabidri (2026–2027)  
> **Target Scope:** ~150–250 lines concise synthesis of verified architecture, pipelines, algorithms, and rules.

---

## 1. Project Title & Overview
- **Project Title:** Food Label Verification System (Do NOT use "SafeBite" or other branding).
- **Domain:** Applied Computer Vision, WebAssembly Optical Character Recognition (OCR), Rule-Based Expert Systems, and Health Informatics.
- **Overview:** A decoupled, web-based platform that parses commercial packaged food labels, identifies chemical additives and allergens, and verifies them against personalized consumer health profiles with transparent confidence estimation.

## 2. Problem Statement & Objectives
- **Problem Statement:** Food manufacturers declare chemical additives using cryptic regulatory numbering (INS / E-numbers) in microscopic fonts across distorted or curved packaging. Generic front-of-package systems lack individualization for specific allergies or diets, while commercial scanner apps rely on unexplainable "black-box" scores without regulatory backing or audit mechanisms.
- **Objectives:** (1) Implement an OpenCV 8-stage image preprocessor to enhance packaging legibility. (2) Provide dual-configuration OCR comparison (Config A: Raw vs. Config B: Preprocessed). (3) Build an authoritative 750-entry INS taxonomy. (4) Develop a deterministic, explainable dietary preference & 11-class allergen matching engine. (5) Implement an Actionable Counterfactual Engine for formulation improvements. (6) Deploy a Human-in-the-Loop (HITL) audit queue for unmapped tokens.

## 3. Actual System Architecture
- **Architecture Style:** Client-Server decoupled architecture.
- **Client (Frontend):** React 18 SPA (`frontend/`) running in browser; handles webcam capture (`react-webcam`), WebAssembly client-side OCR (`tesseract.js`), and Axios API communication with auto-retry (`localhost` to `127.0.0.1`).
- **Server (Backend):** Python Flask WSGI REST API (`backend/app.py`, 1297 lines, 26 routes) hosting 11 modular services.
- **Storage & Data:** Local SQLite 3 (`backend/data/app.db`), static JSON knowledge bases (`ins_taxonomy.json` - 750 entries, `regulatory_references.json` - 22 entries), and dynamic audit log (`unmapped_additives.json`).

## 4. Two Main Processing Pipelines (Strictly Decoupled)
1. **Product Identification Pipeline:** Barcode input (webcam image via OpenCV `BarcodeDetector` or manual 13-digit string) $\to$ EAN-13 Modulo-10 checksum validation $\to$ Open Food Facts REST API lookup (with 4.0s timeout and offline fallback catalog `BENCHMARK_PRODUCTS`) $\to$ Retrieves brand, product name, categories, and macronutrients.
2. **Personalised Dietary Analysis Pipeline:** Label capture (upload/webcam) $\to$ Server OpenCV 8-stage preprocessing $\to$ Tesseract OCR text extraction $\to$ Ingredient boundary isolation (`identify_ingredient_section`) $\to$ INS taxonomy regex & synonym parsing $\to$ Dietary preference & allergen matching $\to$ Personalised Suitability Score (0–100) and allergen alerts.
*CRITICAL ARCHITECTURAL FACT:* The two pipelines operate **independently**. The system **deliberately does NOT perform direct cross-source ingredient mismatch detection** between OCR text and Open Food Facts database records.

## 5. Verified Technology Stack
- **Languages & Runtimes:** Python 3.10+ (tested on 3.14), JavaScript (ES6+ / JSX), Node.js 18+, SQLite 3 embedded.
- **Backend Frameworks:** Flask 3.1.3, Flask-CORS 6.0.2, Werkzeug 3.1.8 (crypto/security), Requests 2.31.0, python-dotenv 1.2.2.
- **Computer Vision & Math:** OpenCV (`opencv-python` 4.13.0), NumPy 2.4.5.
- **Frontend Libraries:** React 18.2.0, React-DOM 18.2.0, Axios 1.6.0, Tesseract.js 5.0.0, react-webcam 7.2.0, Recharts 2.10.0, Lucide React 0.300.0.
- **Testing:** Python `unittest` / `pytest` (187 passing automated tests).

## 6. Important Modules & Responsibilities
- `backend/services/auth_service.py`: PBKDF2:SHA256 password hashing, 64-hex token sessions, 5 dietary presets, custom preference overrides.
- `backend/services/barcode.py`: Modulo-10 checksum validation, Open Food Facts HTTP query, offline fallback catalog.
- `backend/services/barcode_decoder.py`: OpenCV `BarcodeDetector` with 0°, 90°, 180°, 270° rotation decoding; returns discrete status.
- `backend/services/ocr/image_preprocessor.py`: 8-stage OpenCV filtering, blur variance estimation, memory guards (max 25MB, 25MP).
- `backend/services/ocr/ocr_pipeline.py`: Dual-configuration manager (Config A: Raw vs. Config B: Preprocessed) with auto-fallback.
- `backend/services/ocr/ocr_comparator.py`: Levenshtein edit distance, character similarity, confusion fix detection (`1NS` $\to$ `INS`, etc.).
- `backend/services/ocr_service.py`: Facade, boundary regex (`ingredients:` to terminators), OCR safety gate.
- `backend/services/parser.py`: INS regex extraction, E-number mapping, synonym lookup, strict MSG rule, ambiguous code advisories.
- `backend/services/preference_engine.py`: Personalised 0–100 score, animal-derived additive detection, 11 allergen keyword detection.
- `backend/services/scoring_engine.py`: Universal rule-based food safety indicator score ($90.0 - \sum \text{penalties}$).
- `backend/services/counterfactual.py`: Actionable formulation optimization simulating additive removal for scores $< 75$.
- `backend/services/audit.py`: HITL audit queue persistence, reviewer action processing (`confirm`, `reject`, `correct`).
- `backend/services/regulatory_checker.py`: Static regulatory database lookups (FSSAI, EFSA, Codex, FDA).
- `backend/services/personal_scoring.py`: User scan history CRUD and JSON export.

## 7. OCR & Image-Processing Methodology
- **OpenCV 8-Stage Pipeline:** (1) Input bound validation; (2) Laplacian blur variance ($\text{Var}(\nabla^2 I) < 70.0$ flagged); (3) Aspect-ratio resizing (upscale $< 1200\times 900$ to width 2000px via cubic interpolation); (4) Grayscale conversion; (5) Bilateral filtering ($d=9, \sigma=75$); (6) CLAHE local contrast enhancement (clip limit 2.5, $8\times 8$ grid); (7) Unsharp masking edge sharpening ($1.5 \times \text{orig} - 0.5 \times \text{blur}$); (8) Otsu adaptive thresholding.
- **Dual Configuration:** Config A (Raw Image $\to$ Tesseract) vs. Config B (OpenCV Preprocessed $\to$ Tesseract).
- **OCR Safety Gate:** Blocks definitive scoring if blur variance $< 70.0$ or mean word confidence $< 0.70$.

## 8. Barcode Identification Methodology
- **Detection:** `cv2.barcode.BarcodeDetector` scanning original and rotated frames.
- **Checksum:** Modulo-10 algorithm: odd digits $\times 1$, even digits $\times 3$; check digit $= (10 - (\text{sum} \pmod{10})) \pmod{10}$.
- **Discrete Status Reporting:** Reports `valid_ean13`, `invalid_checksum`, `not_detected`, `decoding_error`. Does **not** invent floating-point confidence values.

## 9. INS Taxonomy & Additive Identification
- **Dataset:** 750 verified additives in `backend/data/ins_taxonomy.json` with code, name, category, hazard level, weight, and synonyms.
- **Regex Normalization:** Captures `INS 102`, `INS:102`, `INS-102`, `INS 500(i)`. Normalizes `E102` $\to$ `INS 102`.
- **Strict MSG Rule:** Only identifies Monosodium Glutamate if explicitly stated as MSG or INS 621. Never infers MSG from generic flavorings.
- **Ambiguous Parent Code Advisories:** Flags generic codes: INS 150 (Caramel class unspecified), INS 500 (Carbonate sub-form unspecified), INS 471 (Plant vs animal lipid origin unspecified).

## 10. Dietary Profiles & Preference Matching
- **Presets:** `general_health`, `clean_label`, `vegan`, `strict_vegetarian`, `low_chemical`.
- **Category Avoidance Flags:** Synthetic colors, preservatives, artificial sweeteners, MSG, animal-derived additives.
- **Animal-Derived Additives:** Explicitly identifies Carmine (INS 120), Gelatin (INS 428), Bone Phosphate (INS 542), Beeswax (INS 901), Shellac (INS 904), L-Cysteine (INS 920).
- **11 Allergen Classes:** Peanuts, tree nuts, dairy, gluten, soy, egg, fish, shellfish, sesame, sulfites, mustard.

## 11. Confidence & Verification Mechanisms
- `ocr_confidence`: Float 0.0–1.0 (mean word confidence from Tesseract; 1.0 if text from database).
- `additive_match_confidence`: Float 0.0–1.0 (ratio of detected additive tokens resolved in taxonomy).
- `barcode_decode_status`: String enum (`valid_ean13`, `invalid_checksum`, `not_provided`, `lookup_failed`).
- `product_identity_confidence`: Float (1.0 = valid EAN + product found in OFF; 0.5 = no EAN provided; 0.0 = lookup failed).
- *Distinction:* Confidence represents signal quality/verification status, NOT predictive model accuracy.

## 12. Database Overview & Important Relationships
- **Engine:** SQLite 3 (`backend/data/app.db`) with foreign keys enabled.
- **Entities & Relationships:**
  - `users` (PK: `id`, unique `username`, `email`, `password_hash`).
  - `auth_tokens` (PK: `token`, FK: `user_id` $\to$ `users.id` ON DELETE CASCADE).
  - `dietary_profiles` (PK: `id`, FK: `user_id` $\to$ `users.id` UNIQUE ON DELETE CASCADE, preset and category flags, JSON lists).
  - `analysis_history` (PK: `id`, FK: `user_id` $\to$ `users.id` ON DELETE SET NULL, stores EAN, raw text, scores, alerts, audit summary).

## 13. Important API Endpoints
- `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `POST /api/v1/auth/logout`, `GET /api/v1/auth/me`.
- `GET / PUT /api/v1/profile`, `GET /api/v1/profile/presets`, `POST /api/v1/profile/allergies`.
- `POST /api/v1/analyze`: Full pipeline analysis accepting `{text, ean, ocr_confidence, product}`.
- `GET /api/v1/product/<barcode>`: Barcode lookup via Open Food Facts.
- `POST /api/v1/barcode/decode`: OpenCV image-based barcode detection.
- `POST /api/v1/ocr/preprocess`: OpenCV 8-stage image enhancement endpoint.
- `POST /api/v1/ocr/compare`: Evaluates Config A vs Config B with Levenshtein edit distance.
- `GET /api/v1/audit/unmapped`, `POST /api/v1/audit/<id>/review`: HITL review queue and actions.
- `GET / DELETE /api/v1/history`, `GET /api/v1/history/export`: History management and JSON export.

## 14. Actual Algorithms & Processing Techniques
- **Modulo-10 Barcode Checksum:** Deterministic mathematical validation of EAN-13 barcodes.
- **OpenCV Filtering:** Bilateral edge-preserving filter, CLAHE local histogram equalization, unsharp masking.
- **Normalized Levenshtein Similarity:** $\text{Similarity} = 1.0 - (\text{LevenshteinDistance} / \max(\text{len}(s_1), \text{len}(s_2)))$.
- **Rule-Based Scoring Formula:** $\text{Score} = 90.0 - \sum \text{AdditivePenalties} - \sum \text{NutrientPenalties}$ (Sodium $>0.4\text{g}$, Sugar $>10\text{g}$, Sat Fat $>4\text{g}$). *Not an ML model; SHAP terminology removed.*
- **Actionable Counterfactual Simulation:** Greedy search simulating removal/substitution of highest-penalty additive for scores $< 75$.

## 15. Implementation Status of Major Features
- **Fully Implemented & Verified:** EAN-13 validation, OpenCV barcode detection, Open Food Facts lookup, OpenCV 8-stage preprocessor, client-side Tesseract OCR, dual-configuration comparison, 750-entry taxonomy parser, strict MSG rule, ambiguous code advisories, deterministic 0–100 scoring, 11 allergen detection, counterfactual engine, HITL audit queue, PBKDF2:SHA256 auth, SQLite history persistence, clinical health-tech React UI, 187 passing automated tests.
- **Implemented but Needs Improvement:** Regulatory references database (functional with 22 static verified entries across FSSAI/EFSA/Codex/FDA; could be expanded).
- **Deliberately Omitted / Not Implemented:** Direct cross-source ingredient mismatch detection between OCR text and Open Food Facts records.
- **Not Implemented:** Deep learning predictive health models, laboratory chemical testing, microbiological safety guarantees.

## 16. Research Contribution & Academic Positioning
- **Gap G1 Addressed:** Neutralizes physical packaging image degradation via an 8-stage OpenCV computer vision preprocessor.
- **Gap G2 Addressed:** Resolves the lack of consumer actionability through an Actionable Counterfactual Engine.
- **Gap G3 Addressed:** Prevents silent recognition failures of new additives via a Human-in-the-Loop audit protocol.
- **Positioning:** An informational and personalized verification tool, not a clinical diagnostic or regulatory enforcement device.

## 17. Limitations
1. In-browser Tesseract.js execution speed depends on client hardware.
2. Severely crumpled foil packages or extreme specular highlights can drop OCR confidence below the 0.70 safety threshold.
3. Language support is limited to English, European Latin, and romanized script (e.g., *samagri*); non-Latin scripts (Devanagari, Tamil) are not supported.
4. Independent pipeline operation without automated semantic cross-source reconciliation.

## 18. Future Enhancements
1. Integrating on-device quantized neural OCR (Google ML Kit or ONNX-quantized models).
2. Multilingual regional taxonomy expansion for Indian regional languages.
3. Automated semantic cross-source verification comparing physical packaging against cloud database records.
4. Automated regulatory scrapers tracking live FSSAI/EFSA gazettes.

## 19. Important Technical Terminology
- **EAN-13 & Modulo-10:** 13-digit retail barcode standard and its alternating weighted checksum.
- **INS & E-Number:** Codex Alimentarius International Numbering System and European additive nomenclature.
- **CLAHE:** Contrast-Limited Adaptive Histogram Equalization for localized surface contrast balancing.
- **Unsharp Masking:** High-frequency edge enhancement technique subtracting a blurred Gaussian mask.
- **Counterfactual:** Simulated feature intervention determining the minimum change required to improve a score.
- **HITL:** Human-in-the-loop workflow routing unmapped tokens to human reviewers.

---

## CLAUDE REPORT MODIFICATION RULES

When reviewing, modifying, or correcting the 80–90-page MCA major project report, Claude must strictly adhere to the following rules:

1. **Use This Compact Reference as Primary Ground Truth:** Treat this document as the executive technical baseline. For deep-dive implementations, consult `PROJECT_MASTER_REFERENCE.md`, `PROJECT_FEATURE_MATRIX.md`, `PROJECT_TECH_STACK.md`, and `PROJECT_ACADEMIC_REFERENCE.md`.
2. **Preserve University & Institutional Format:** Maintain MITE / VTU thesis styling: Times New Roman, 12pt body, 1.5 line spacing, 3.5 cm left margin, 2.54 cm right/top/bottom margins, lowerRoman prelims (Pages i–xi), Arabic chapter pagination (Pages 1–73).
3. **Preserve Exact Project Naming:** Use only **Food Label Verification System**. Never re-introduce "SafeBite" or alternative brand names.
4. **Never Fabricate Technical Capabilities:**
   - Do **NOT** claim the system uses deep learning or machine learning for scoring. Scoring is strictly **deterministic and rule-based**.
   - Do **NOT** use the term "SHAP" or claim Shapley value calculation.
   - Do **NOT** claim the system performs cross-source comparison between OCR text and Open Food Facts records.
   - Do **NOT** claim laboratory food safety certification or medical diagnosis.
5. **Accurately Report Test Figures:** The automated test suite consists of **187 passing unit and integration tests** executed via Python `unittest` / `pytest` with a 100% pass rate.
6. **Preserve Figure and Table Layouts:** Retain the reserved placeholder boxes for all 32 figures and 11 formal technical tables without breaking pagination.
7. **Target Page Count:** Ensure any expanded or revised chapters keep the final document strictly within **80 to 90 pages** (ideal: 82–85 pages).
