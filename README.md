# Food Label Verification System
### A Confidence-Aware Multimodal Food Label Verification System Using Deep Learning and OCR

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![React Version](https://img.shields.io/badge/react-18.2.0-blue.svg)](https://react.dev/)
[![Test Suite](https://img.shields.io/badge/tests-154%20passed%20(100%25)-brightgreen.svg)](tests/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 1. System Overview & Philosophy

The **Food Label Verification System** is an end-to-end multimodal packaged food verification and dietary safety system designed for research and consumer protection. It addresses critical limitations in existing barcode-lookup applications by decoupling catalog product identity from physical label verification, implementing computer vision preprocessing with OCR uncertainty gating, and providing transparent rule-based dietary evaluations.

### Core Architectural Principle: Decoupled Multimodal Pipelines

The system is strictly structured around two independent analytical pipelines:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        FOOD LABEL VERIFICATION                         │
└────────────────────────────────────────────────────────────────────────┘
                                    │
           ┌────────────────────────┴────────────────────────┐
           ▼                                                 ▼
┌───────────────────────────────┐         ┌──────────────────────────────┐
│  PIPELINE A: PRODUCT IDENTITY │         │ PIPELINE B: DIETARY ANALYSIS │
│   (EAN-13 Barcode Scanning)   │         │  (Packaging Image OCR / Text)│
├───────────────────────────────┤         ├──────────────────────────────┤
│ • Modulo-10 Checksum Check    │         │ • Laplacian Blur Detection   │
│ • OpenCV Barcode Localisation │         │ • CLAHE Contrast Enhancement │
│ • Open Food Facts / Benchmark │         │ • OCR Safety Gate (<0.40)    │
│ • Identity Verification Only  │         │ • INS Taxonomy Parsing       │
│                               │         │ • Allergen & Preference Match│
│                               │         │ • Personal Suitability Score │
└───────────────────────────────┘         └──────────────────────────────┘
```

> **Important Design Decision:** Automatic cross-comparison between database ingredients and OCR-extracted ingredients is intentionally omitted. Regional formulation differences, repackaging variations, and OCR transcription artifacts cause high false-mismatch rates. Instead, the physical packaging label is treated as the ground truth for consumer consumption, and database records serve strictly for product identity verification.

---

## 2. Key Modules & Technical Capabilities

### Module 1: Comprehensive INS Taxonomy Engine (`backend/services/parser.py`)
- Maps food additives against a verified taxonomy of **750+ mapped keys** and **250+ unique food additives** (`backend/data/ins_taxonomy.json`).
- Handles complex regulatory notations: parenthetical category numbers (e.g., `Colour (102, 110)`), INS prefixes (`INS 211`), European E-numbers (`E250`), and alternative chemical synonyms.
- Multi-functional classification support: accurately indexes additives serving multiple roles (e.g., `INS 300` as both Antioxidant and Flour Treatment Agent).
- Distinguishes color origins (natural vs. synthetic) and enforces strict Monosodium Glutamate (MSG) disambiguation.
- Ambiguous parent code reporting (e.g., generic `INS 150` Caramel flagged for expert review when class a/b/c/d is unstated).

### Module 2: Computer Vision & OCR Preprocessing (`backend/services/ocr_service.py`)
- **Laplacian Blur Detection:** Computes variance of the Laplacian ($< 70.0$ threshold) to detect out-of-focus or motion-blurred packaging labels.
- **CLAHE Contrast Enhancement:** Contrast Limited Adaptive Histogram Equalization normalizes illumination across curved and glossy plastic/foil food packaging.
- **Unsharp Masking:** High-frequency sharpening filter accentuates small print fonts on ingredient declarations.
- **Clause Isolation & Boundary Detection:** Identifies the core `INGREDIENTS:` section and strips trailing manufacturer declarations, certifications, and marketing copy.
- **Parenthesis-Aware Ingredient Splitting:** Prevents false segmentation inside nested additive declarations (e.g., `Thickeners (INS 508, INS 412)` remains a single compound clause).
- **OCR Safety Gate:** When mean word-level OCR confidence drops below $40\%$ or text clarity is degraded, definitive dietary verdicts are suppressed and flagged as provisional.

### Module 3: Deterministic Rule-Based Safety Scoring (`backend/services/scoring_engine.py`)
- Computes public health baseline safety score on a 0–100 scale (Grades A to D) from a whole-food baseline ($90.0$ points).
- Transparent, explainable point deductions based on established EFSA, FSSAI, and WHO hazard classifications.
- Zero black-box machine learning or fabricated feature attribution claims.
- Actionable Counterfactual Engine (`backend/services/counterfactual.py`) simulates formulation improvements when safety score $< 75$.

### Module 4: Personalised Dietary Preference Engine (`backend/services/preference_engine.py`)
- User-specific dietary profiles with standard presets: `Clean Label`, `Vegan`, `Vegetarian`, `Child-Safe`, `Low Chemical`, `Nut Free`.
- Granular category avoidance toggles: synthetic colors, chemical preservatives, artificial sweeteners, flavor enhancers, animal derivatives.
- Custom avoid and caution lists by individual INS numbers.
- **Zero-Compromise Allergen Safety Cap:** Detecting configured allergens immediately caps personal score at $\le 20$ points, triggers high-contrast warnings, and prevents false-negative safety assurance.

### Module 5: Human-in-the-Loop (HITL) Audit Protocol (`backend/services/audit.py`)
- Evaluates 4 independent confidence dimensions:
  1. `ocr_confidence` (Float 0.0–1.0): Mean word-level Tesseract confidence.
  2. `additive_match_confidence` (Float 0.0–1.0): Fraction of detected tokens resolved in taxonomy.
  3. `barcode_decode_status` (Categorical Enum): `valid_ean13`, `invalid_checksum`, `lookup_failed`, `not_provided`.
  4. `product_identity_confidence` (Float 0.0–1.0): Verification degree of barcode record.
- Flags unmapped chemical tokens for expert review and maintains an active learning queue with reviewer actions (`confirm`, `reject`, `correct`).

### Module 6: Persistent Scan History & User Session Management (`backend/services/personal_scoring.py`)
- SQLite persistence schema: `users`, `auth_tokens`, `dietary_profiles`, `analysis_history`.
- Cryptographic security: PBKDF2:SHA256 password hashing and 30-day bearer token sessions.
- Scan history management: multi-parameter search, verdict filtering, allergen isolation, server-side pagination, single-record deletion, clear all, and streaming data export (JSON/CSV).

---

## 3. System Architecture & Directory Structure

```
d:/food-risk-checker/
├── backend/
│   ├── app.py                      # Main Flask API routing & controllers (18+ endpoints)
│   ├── requirements.txt            # Python dependencies
│   ├── data/
│   │   ├── app.db                  # SQLite persistent database
│   │   ├── ins_taxonomy.json       # Master INS chemical taxonomy (750+ keys)
│   │   ├── regulatory_references.json # FSSAI / EFSA regulatory status
│   │   └── unmapped_additives.json # HITL audit records log
│   ├── models/
│   │   ├── database.py             # Schema DDL, connections, auto-migrations
│   │   ├── user.py                 # User domain entity model
│   │   └── profile.py              # DietaryProfile domain entity model
│   └── services/
│       ├── auth_service.py         # Registration, PBKDF2 authentication, token sessions
│       ├── preference_engine.py    # Dietary profile matching & allergen cap engine
│       ├── scoring_engine.py       # Rule-based safety scoring & deductions
│       ├── counterfactual.py       # Reformulation suggestions
│       ├── parser.py               # INS extraction, synonym resolution, duplicate consolidation
│       ├── ocr_service.py          # CV preprocessing, blur detection, CLAHE, safety gate
│       ├── barcode.py              # EAN-13 validation & Open Food Facts client
│       ├── barcode_decoder.py      # OpenCV image-based barcode detection
│       ├── regulatory_checker.py   # Regulatory database queries
│       ├── audit.py                # HITL audit evaluation & queue management
│       └── personal_scoring.py     # History queries, pagination, and JSON/CSV export
├── frontend/
│   ├── public/
│   │   └── index.html              # HTML shell
│   ├── src/
│   │   ├── App.js                  # Main dashboard orchestration
│   │   ├── api.js                  # Axios HTTP client
│   │   ├── style.css               # Glassmorphism design system
│   │   └── components/
│   │       ├── BarcodeScanner.jsx          # Mode 1: EAN-13 barcode scanner & benchmarks
│   │       ├── CameraScanner.jsx           # Mode 2: Live camera scanner with guide frame
│   │       ├── ImageUpload.jsx             # Mode 3: Drag & drop packaging image upload
│   │       ├── IngredientTextInput.jsx     # Mode 4: Manual text input & quick parsing
│   │       ├── SafetyScoreCard.jsx         # Public health safety indicator
│   │       ├── PersonalisedScoreCard.jsx   # Personal dietary assessment & allergen alerts
│   │       ├── ConfidencePanel.jsx         # 4-way confidence & telemetry indicators
│   │       ├── ShapAttributionChart.jsx    # Rule-based score deductions breakdown
│   │       ├── CounterfactualCard.jsx      # Actionable reformulation recommendations
│   │       ├── AuthModal.jsx               # User login & registration
│   │       ├── DietaryProfileModal.jsx     # Presets, category toggles & custom INS lists
│   │       ├── AnalysisHistoryModal.jsx    # Scan history search, filter, inspect & export
│   │       └── AuditQueueModal.jsx         # HITL reviewer queue & statistics
└── tests/
    ├── test_stage2_services.py             # 80 tests: scoring, parser, audit, regulatory
    ├── test_auth_and_preferences.py        # 12 tests: PBKDF2 auth, token lifecycle, presets
    ├── test_full_system.py                 # 12 tests: barcode decoder, end-to-end integration
    ├── test_preference_engine.py           # 13 tests: allergen cap, category avoidance, deductions
    ├── test_ocr_service.py                 # 13 tests: blur detection, CLAHE, clause isolation
    ├── test_ins_parser_refinements.py      # 14 tests: parenthetical categories, MSG, synonyms
    ├── test_history_and_audit.py           # 10 tests: history search, pagination, export, audit stats
    └── test_xai_framework.py               # 8 tests: baseline validation
```

---

## 4. API Reference Documentation

All endpoints are hosted at `http://localhost:5005` (with fallback to `http://127.0.0.1:5005`).

### 4.1 Authentication & Profile Endpoints
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `POST` | `/api/v1/auth/register` | Register new user account with default dietary profile | No |
| `POST` | `/api/v1/auth/login` | Authenticate user, returns 30-day Bearer token | No |
| `POST` | `/api/v1/auth/logout` | Revoke active session token | Bearer Token |
| `GET` | `/api/v1/auth/me` | Retrieve authenticated user details and dietary profile | Bearer Token |
| `GET` | `/api/v1/profile` | Retrieve active user dietary profile | Bearer Token |
| `POST` | `/api/v1/profile` | Update dietary profile settings | Bearer Token |
| `GET` | `/api/v1/profile/preferences` | Retrieve granular category & INS preferences | Bearer Token |
| `POST` | `/api/v1/profile/preferences/categories` | Update category avoidance toggles | Bearer Token |
| `POST` | `/api/v1/profile/preferences/additives` | Add/remove INS codes from avoid or caution list | Bearer Token |
| `POST` | `/api/v1/profile/allergies` | Add, remove, or set active allergen triggers | Bearer Token |
| `GET` | `/api/v1/profile/presets` | List predefined dietary profiles (Vegan, Clean Label, etc.) | No |
| `POST` | `/api/v1/preferences/evaluate` | Standalone evaluation of text/additives against profile | Optional |

### 4.2 Verification & Computer Vision Endpoints
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/analyze` | Unified verification pipeline (Barcode or OCR text + Dietary Profile) |
| `GET` | `/api/v1/product/<barcode>` | EAN-13 checksum validation and product catalog lookup |
| `POST` | `/api/v1/barcode/decode` | OpenCV image-based barcode detection (file upload or base64) |
| `POST` | `/api/v1/ocr/preprocess` | OpenCV Laplacian blur check, CLAHE enhancement, unsharp mask |
| `POST` | `/api/v1/ocr/extract-section` | Regex ingredient section extraction and clause isolation |
| `POST` | `/api/v1/parser/parse` | Direct additive detection, category grouping, and ambiguity check |

### 4.3 History & HITL Audit Endpoints
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `GET` | `/api/v1/history` | List scan history with search, verdict, allergen filters & pagination | Bearer Token |
| `GET` | `/api/v1/history/<id>` | Retrieve full single scan details (raw text, additives, allergens) | Bearer Token |
| `DELETE` | `/api/v1/history/<id>` | Delete individual scan record | Bearer Token |
| `DELETE` | `/api/v1/history` | Clear all scan history for the authenticated user | Bearer Token |
| `GET` | `/api/v1/history/export` | Export scan history as streaming JSON or CSV file | Bearer Token |
| `GET` | `/api/v1/audit/unmapped` | List unmapped chemical tokens pending human review | No |
| `GET` | `/api/v1/audit/stats` | Aggregated audit queue metrics (total, pending, confirmed, corrected) | No |
| `POST` | `/api/v1/audit/<id>/review` | Submit reviewer action (`confirm`, `reject`, `correct`) | No |
| `DELETE` | `/api/v1/audit/<id>` | Dismiss/delete an audit queue record | No |
| `GET` | `/api/health` | Service health and engine version check | No |

---

## 5. Installation & Setup Instructions

### Prerequisites
- **Python:** 3.10 or higher (tested on Python 3.10, 3.11, 3.12, 3.14)
- **Node.js:** v16.x or higher (npm v8+)
- **OS:** Windows, macOS, or Linux

### Step 1: Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/example/food-label-verification-system.git
cd food-label-verification-system

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### Step 2: Install Backend Dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 3: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## 6. Execution & Deployment Guide

### Running the Backend Service
From the project root:
```bash
python backend/app.py
```
*The Flask API server starts on `http://localhost:5005` (with SQLite database auto-initialized at `backend/data/app.db`).*

### Running the Frontend Application (Development Mode)
In a separate terminal:
```bash
cd frontend
npm start
```
*The React application opens in your browser at `http://localhost:3000`.*

### Building Frontend for Production
```bash
cd frontend
npm run build
```
*Compiles static production assets to `frontend/build/` with zero warnings or errors.*

---

## 7. Verification & Test Suite

The system includes a comprehensive unit and integration test suite comprising **154 automated tests** with 100% pass coverage.

To run all tests from the project root:
```bash
python -m unittest discover tests -v
```

### Test Suite Breakdown:

| Test Module | Tests | Scope | Status |
| :--- | :---: | :--- | :---: |
| [`tests/test_stage2_services.py`](tests/test_stage2_services.py) | 80 | Rule-based scoring, parser validation, regulatory lookups, 4-way confidence | **PASS** |
| [`tests/test_auth_and_preferences.py`](tests/test_auth_and_preferences.py) | 12 | PBKDF2 password hashing, token lifecycle, presets, dietary profiles | **PASS** |
| [`tests/test_full_system.py`](tests/test_full_system.py) | 12 | End-to-end API integration, OpenCV barcode decoder, OCR safety gates | **PASS** |
| [`tests/test_preference_engine.py`](tests/test_preference_engine.py) | 13 | Allergen safety cap ($\le 20$), category avoidance, deduction rationale | **PASS** |
| [`tests/test_ocr_service.py`](tests/test_ocr_service.py) | 13 | Laplacian blur variance, CLAHE contrast, clause isolation, safety gate | **PASS** |
| [`tests/test_ins_parser_refinements.py`](tests/test_ins_parser_refinements.py) | 14 | Parenthetical categories, strict MSG rule, duplicate consolidation | **PASS** |
| [`tests/test_history_and_audit.py`](tests/test_history_and_audit.py) | 10 | History search, pagination, delete, CSV/JSON export, audit statistics | **PASS** |
| **Total** | **154** | **Complete System Verification** | **100% OK** |

---

## 8. Research Evaluation Plan

This system was developed as an MCA Major Project addressing the research question:
> *Can confidence-aware multimodal verification using decoupled barcode identification and OCR preprocessing improve food label consistency and consumer safety over traditional single-source lookups?*

### Evaluation Metrics:
1. **Extraction Accuracy:** Precision and Recall of additive extraction across varying image qualities (sharp vs. motion-blurred).
2. **False Positive Suppression:** Rate of false alarms prevented by parenthesis-aware clause isolation and strict MSG disambiguation.
3. **Allergen Sensitivity:** 100% detection rate on configured allergens with mandatory score capping to $\le 20$.
4. **OCR Gate Effectiveness:** Verification that degraded images ($< 0.40$ confidence or blur variance $< 70.0$) trigger provisional score alerts.

---

## 9. License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
