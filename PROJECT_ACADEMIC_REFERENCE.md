# Food Label Verification System — Academic & Research Reference

This document provides a grounded academic reference for the MCA Major Project titled **Food Label Verification System**. It articulates the exact problem statement, research contributions, architectural boundaries, and factual distinctions required for academic evaluation.

---

## 1. Project Identification
- **Project Title:** Food Label Verification System
- **Academic Degree:** Master of Computer Applications (MCA)
- **Institution:** Mangalore Institute of Technology & Engineering (MITE), Moodabidri
- **Academic Year:** 2026–2027
- **Primary Domain:** Applied Computer Vision, Optical Character Recognition, Rule-Based Expert Systems, and Health Informatics.

---

## 2. Abstract
Modern ultra-processed food products frequently contain complex combinations of chemical additives, synthetic colorants, preservatives, and concealed allergens. Although international food regulatory authorities (FSSAI, EFSA, Codex Alimentarius) mandate the disclosure of ingredients on food packaging, consumers with specific metabolic conditions, severe food allergies, or ethical dietary regimens struggle to decipher dense, microscopic, and technically coded ingredient lists (e.g., International Numbering System codes such as INS 102, INS 211, INS 250).

The **Food Label Verification System** addresses this challenge through a decoupled, confidence-aware dual-pipeline architecture. The **Product Identification Pipeline** utilizes native OpenCV barcode detection (`cv2.barcode.BarcodeDetector`) and deterministic Modulo-10 checksum validation to identify packaged products and fetch authoritative nutritional data via the Open Food Facts API. Concurrently, the **Personalised Dietary Analysis Pipeline** employs a high-fidelity OpenCV 8-stage image preprocessor (aspect-ratio resizing, bilateral filtering, CLAHE contrast equalization, unsharp masking, and Otsu binarization) combined with client-side Tesseract OCR to extract packaging text. Extracted text is parsed against an authoritative local 750-entry INS taxonomy using token-based regex and synonym mapping. Identified additives and allergens are matched against user-customized dietary profiles to generate a transparent, deterministic **Personalised Suitability Score (0–100)** and critical allergen alerts. An Actionable Counterfactual Engine simulates formulation interventions to recommend health-improving substitutions, while a Human-in-the-Loop (HITL) audit queue flags unmapped tokens for manual verification. The system is validated across 187 automated test cases, delivering an explainable, robust, and consumer-centric food safety verification solution.

---

## 3. Problem Statement
Commercial food packaging often presents significant barriers to transparent consumer comprehension:
1. **Cryptic Regulatory Coding:** Food manufacturers denote chemical preservatives, artificial sweeteners, and stabilizers using numerical INS and E-number codes rather than transparent descriptive names.
2. **Microscopic Font & Packaging Distortion:** Packaging labels feature low-contrast, non-planar, curved, or reflective surfaces that degrade standard optical character recognition.
3. **Absence of Personalization:** Universal front-of-package warning labels fail to account for individualized physiological restrictions, such as specific food allergies (celiac disease, lactose intolerance) or ethical diets (veganism, clean label).
4. **Lack of Explainability & Verification Gaps:** Existing commercial applications provide black-box health ratings without regulatory citations, actionability, or mechanisms to audit unmapped or misread ingredients.

---

## 4. Objectives and Scope

### Primary Objectives:
1. **Develop an OpenCV 8-Stage Image Preprocessing Pipeline:** Neutralize real-world packaging degradations (uneven lighting, motion blur, curved surfaces) to improve OCR character recognition.
2. **Implement Dual-Configuration OCR Verification:** Provide comparative evaluation between raw Tesseract OCR (Config A) and OpenCV-preprocessed Tesseract OCR (Config B) using Levenshtein distance and character confusion fixes.
3. **Construct an Authoritative 750-Entry INS Additive Taxonomy:** Categorize food additives by functional class, hazard level, permitted status, and known synonyms according to Codex Alimentarius and FSSAI standards.
4. **Engine Deterministic Dietary Preference & Allergen Matching:** Evaluate detected ingredients against user-defined profiles to compute a 0–100 Personalised Suitability Score and detect 11 major allergen categories.
5. **Formulate Actionable Counterfactual Explanations:** Provide simulated formulation improvements demonstrating the exact score gain achievable by removing or substituting high-risk additives.
6. **Establish Human-in-the-Loop (HITL) Audit Protocol:** Capture unmapped candidate additive tokens to prevent silent recognition failures and maintain taxonomic integrity.

### Scope Boundaries:
- **Informational and Personalised Tool:** The system serves as an informational consumer aid; it does **not** perform clinical food safety certification, laboratory chemical verification, or microbiological hazard assessment.
- **Decoupled Pipelines:** The Product Identification Pipeline (barcode) and Personalised Dietary Analysis Pipeline (OCR) operate independently. The system **deliberately does not perform direct cross-source ingredient mismatch detection** between OCR text and Open Food Facts database records.

---

## 5. Distinction Between Methodologies: AI/ML vs. Rule-Based

To ensure academic rigor, the technological foundations of the system are categorized accurately:

| System Operation | Underlying Methodology | Description |
|---|---|---|
| Optical Character Recognition | Machine Learning / Deep Learning (OCR) | Tesseract LSTM neural network extracting text glyphs and assigning word-level confidence values. |
| Image Preprocessing & Barcode Decoding | Computer Vision (OpenCV) | Deterministic matrix transformations (CLAHE, bilateral filter, unsharp mask) and gradient barcode edge detection. |
| INS & E-Number Identification | Rule-Based Regex & Token Matching | Regular expressions and multi-token sliding window lookup against a 750-entry static JSON taxonomy. |
| Dietary Preference Scoring | Deterministic Rule-Based Algorithm | Arithmetic penalty deductions based on hazard weights and user-defined category avoidance flags. **Not an ML model; no Shapley values.** |
| Counterfactual Intervention | Heuristic Optimization | Greedy search identifying the highest-penalty additive and re-evaluating the scoring function on a simulated formulation. |
| Barcode Checksum | Mathematical Algorithm | Standard Modulo-10 checksum validation with alternating 1 and 3 weights. |

---

## 6. Research Gaps Addressed

The system addresses three critical research gaps identified in contemporary food informatics literature:

1. **Gap G1 — Image Degradation in In-the-Wild Label Capture:** Standard OCR engines suffer significant character error rates on curved foil and plastic food packages. The system introduces an 8-stage OpenCV preprocessor (CLAHE + unsharp masking) to stabilize text binarization.
2. **Gap G2 — Lack of Actionable Consumer Guidance:** Traditional scoring systems output a static grade without guidance on how to improve. The Counterfactual Engine simulates ingredient removal, providing actionable advice (e.g., *"Remove INS 250 to gain +18.5 points"*).
3. **Gap G3 — Silent Failures in Unmapped Additive Detection:** Traditional regex systems discard unmapped tokens silently. The HITL Audit Protocol captures unmapped tokens in an audit log, allowing human reviewers to confirm, reject, or correct new chemical synonyms.

---

## 7. Limitations & Future Scope

### Verified Technical Limitations:
- **Client-Side Processing Overhead:** In-browser Tesseract.js execution on low-powered mobile devices can incur higher extraction latency compared to native GPU backends.
- **Extreme Packaging Deformations:** Severely crumpled packaging or cylindrical foil wraps with extreme specular highlights can still degrade OCR confidence below the 0.70 safety threshold.
- **Language Scope:** The current OCR and taxonomy parsing pipeline is optimized for English, European Latin, and romanized script (e.g., *samagri*). Non-Latin regional scripts (Devanagari, Tamil) are not currently supported.
- **Independent Pipeline Operation:** No automated semantic cross-validation is performed between the Open Food Facts ingredient list and the live scanned OCR text.

### Future Scope:
1. **Edge-Optimized Native OCR:** Integrating lightweight on-device models (e.g., Google ML Kit or ONNX-quantized MobileNet OCR) to reduce client latency.
2. **Multilingual Regional Parsing:** Expanding the taxonomy to include native Indian regional scripts (Hindi, Kannada, Telugu) as mandated by expanding FSSAI regional labeling initiatives.
3. **Automated Cross-Source Reconciliation:** Implementing semantic similarity algorithms to compare physical packaging OCR against cloud database ingredient records to identify counterfeit or reformulated goods.
