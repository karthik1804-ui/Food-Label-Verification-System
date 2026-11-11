# PROJECT_ANALYSIS.md
## SafeBite → SafeBite 2.0: Comprehensive Project Analysis
**Analyst:** Stage 1 Review | **Date:** 2026-11-02 | **Scope:** `d:\food-risk-checker\`

---

## 1. Existing Architecture

### Technology Stack

| Layer | Technology | Version |
|---|---|---|
| Backend server | Flask | ≥3.0.0 |
| Backend language | Python | 3.14 |
| CORS | flask-cors | ≥4.0.0 |
| HTTP client | urllib.request (stdlib) | — |
| Frontend | React (CRA) | 18.2.0 |
| Frontend build | react-scripts | 5.0.1 |
| OCR engine | Tesseract.js (in-browser) | ^5.0.0 |
| Charts | Recharts | ^2.10.0 |
| HTTP client (FE) | Axios | ^1.6.0 |
| Icons | lucide-react | ^0.300.0 |
| Camera access | react-webcam | ^7.2.0 |
| Listed ML deps | scikit-learn, xgboost, shap, numpy, pandas | in requirements.txt only |

### Directory Structure (Current)

```
d:\food-risk-checker\
├── backend/
│   ├── app.py                        ← Flask server (294 lines, 7 routes)
│   ├── requirements.txt              ← Python dependencies
│   ├── data/
│   │   ├── ins_taxonomy.json         ← 750+ additive entries (313 KB)
│   │   └── unmapped_additives.json   ← Audit log (active, 74 lines)
│   └── services/
│       ├── barcode.py                ← EAN-13 validator + OFF API
│       ├── parser.py                 ← INS/E-number regex parser
│       ├── scoring_engine.py         ← Rule-based "SHAP" scorer
│       ├── counterfactual.py         ← Rule-based counterfactual
│       └── audit.py                  ← HITL audit logger
├── frontend/
│   ├── package.json
│   ├── public/index.html
│   ├── build/                        ← Pre-built static files
│   └── src/
│       ├── App.js                    ← Main dashboard (356 lines)
│       ├── api.js                    ← Axios client (57 lines)
│       ├── index.js
│       ├── style.css                 ← Glassmorphism dark theme (20 KB)
│       └── components/
│           ├── BarcodeScanner.jsx    ← EAN-13 text input + chips
│           ├── SafetyScoreCard.jsx   ← SVG gauge + grade
│           ├── ShapAttributionChart.jsx ← Horizontal bar chart
│           ├── CounterfactualCard.jsx ← Counterfactual display
│           ├── AuditStatusBadge.jsx  ← Confidence bar + HITL banner
│           ├── AuditQueueModal.jsx   ← Modal: unmapped tokens table
│           ├── CameraScanner.jsx     ← Webcam + autofocus + guide box
│           └── ImageUpload.jsx       ← Drag-and-drop upload
├── tests/
│   └── test_xai_framework.py         ← 8 integration tests
└── README.md
```

### API Endpoints (Current)

| Method | Route | Status |
|---|---|---|
| GET | `/` | ✅ Working |
| GET | `/api/health` | ✅ Working |
| POST | `/api/v1/analyze` | ✅ Working |
| GET | `/api/v1/analyze?ean=...` | ✅ Working |
| GET | `/api/v1/product/<barcode>` | ✅ Working |
| GET | `/api/v1/audit/unmapped` | ✅ Working |
| POST | `/analyze` | ✅ Working (legacy) |

---

## 2. Existing Features

### Fully Implemented and Working

| Feature | File | Notes |
|---|---|---|
| EAN-13 Modulo-10 checksum validation | `barcode.py` | Correct algorithm |
| Benchmark product catalog (4 products) | `barcode.py` | Offline demo fallback |
| Open Food Facts API fetch | `barcode.py` | urllib.request, 4s timeout |
| Regex OCR normalizer (I→1, O→0) | `parser.py` | Two-pass, context-aware |
| INS/E-number token extraction | `parser.py` | Multi-pattern regex |
| Chemical name lookup (20 names) | `parser.py` | Hardcoded dictionary |
| Taxonomy lookup against JSON | `parser.py` | Local file, triple key lookup |
| Numerical feature vector construction | `parser.py` | 20-dimensional vector |
| Rule-based scoring (0–100) | `scoring_engine.py` | Fixed penalties per additive |
| Grading (A–E) | `scoring_engine.py` | Threshold-based |
| Nutrient penalties (WHO thresholds) | `scoring_engine.py` | Sodium, sugar, sat. fat |
| Counterfactual simulation | `counterfactual.py` | Removes worst additive, re-scores |
| HITL audit logging | `audit.py` | JSON file append |
| Audit confidence flagging | `audit.py` | Triggers below 0.85 |
| React dashboard with 3 input tabs | `App.js` | Barcode / Camera / Upload |
| In-browser OCR (Tesseract.js) | `App.js` | PSM 6, English |
| Image preprocessing (sharpening) | `App.js` | Canvas kernel convolution |
| Camera guide overlay | `CameraScanner.jsx` | 70% center crop |
| Drag-and-drop image upload | `ImageUpload.jsx` | FileReader API |
| EAN-13 client-side validation | `BarcodeScanner.jsx` | Live checksum feedback |
| SVG safety score gauge | `SafetyScoreCard.jsx` | Circular, animated |
| SHAP bar chart | `ShapAttributionChart.jsx` | Filter by type |
| Counterfactual UI card | `CounterfactualCard.jsx` | Simulate button |
| Audit status badge | `AuditStatusBadge.jsx` | Confidence % bar |
| Audit queue modal | `AuditQueueModal.jsx` | Displays JSON records |
| CORS headers on all responses | `app.py` | after_request handler |
| 8 integration tests | `test_xai_framework.py` | All passing |

---

## 3. Features That Are Partially Implemented

### 3.1 Scoring Engine — Labelled as SHAP, Not Actually SHAP
**File:** `scoring_engine.py`
**What exists:** Fixed per-additive point deductions (e.g. INS 250 → −18.5 pts). These are hardcoded constants, not Shapley values computed by a trained model.
**What is missing:** An actual trained predictive model (XGBoost, scikit-learn, etc.), a `shap.TreeExplainer` or `shap.KernelExplainer`, and a training dataset.
**Impact:** The word "SHAP" appears in comments, README, and the UI (`ShapAttributionChart.jsx`) but refers to manual deduction rules, not true Shapley values. This is the biggest technical accuracy problem.

### 3.2 Parser Confidence — Computed but Misleading
**File:** `parser.py` → `parse_additives_and_audit()`
**What exists:** `confidence = 0.70 + (0.28 * matched_ratio)` — a linear formula based on how many extracted tokens were found in the taxonomy.
**What is missing:** Actual OCR confidence (Tesseract provides word-level confidence scores), barcode decode confidence, product identity confidence. The current value mixes different uncertainty sources into one number.

### 3.3 Audit HITL — Logging Only, No Review Interface
**File:** `audit.py`, `AuditQueueModal.jsx`
**What exists:** Unmapped tokens are logged to a JSON file. The modal shows them.
**What is missing:** A reviewer cannot currently confirm, reject, or correct a detected token. The "Active Learning" claim in the README is aspirational — no training loop exists.

### 3.4 Counterfactual — Works but Oversimplified
**File:** `counterfactual.py`
**What exists:** Removes the worst additive, re-runs the rule-based scorer, reports the gain.
**What is missing:** The claim "Removing X makes the product healthier" ignores that the additive may serve a preservation function, that the product could not realistically be reformulated this way, and that the rule-based score does not reflect real health evidence. The UI implies this as a medical/safety recommendation.

### 3.5 Taxonomy — Missing Provenance and Source References
**File:** `ins_taxonomy.json`
**What exists:** 750+ entries with code, name, class, hazard_level, hazard_weight, description, common_substitute.
**What is missing:** No `source` field, no `last_verified` date, no reference URL, no `verified` status flag, no distinction between regulatory classification and general health information. Hazard weights appear to be manually assigned without a cited methodology.

### 3.6 OCR Pipeline — Preprocessing Done, No Confidence Forwarded
**File:** `App.js`
**What exists:** Canvas sharpening, cropping, Tesseract.js OCR. The raw text is sent to the backend.
**What is missing:** Tesseract.js provides per-word confidence scores (`res.data.words[].confidence`). These are discarded. The backend never sees OCR confidence — it uses the matched-token ratio as a proxy.

---

## 4. Missing Features (Required for SafeBite 2.0)

### 4.1 Barcode Image Detection — COMPLETELY ABSENT
**Current state:** `BarcodeScanner.jsx` provides a plain text input field where the user types an EAN-13 number manually. There is zero image-based barcode detection anywhere in the codebase.
**What the README implies:** The project description mentions "barcode detection" but this is misleading — it is barcode *number entry* with checksum validation.
**Required for 2.0:** A barcode localisation step (YOLO or equivalent) and a barcode decoding library (ZXing, pyzbar, or similar) to extract the EAN digits from a packaging image.

### 4.2 Multimodal Consistency Verification — ABSENT
No module compares OCR-extracted ingredient information with the Open Food Facts (OFF) reference data retrieved via barcode.
- If a user scans a Maggi noodles packet, the system fetches ingredient text from OFF *and* extracts it via OCR, but never compares whether the two match.
- There is no `product_matcher.py`, no consistency scoring, no mismatch classification.

### 4.3 Anomaly Detection Module — ABSENT
No rule-based or ML-based anomaly detector exists. The audit module detects unmapped tokens (a parsing gap), which is different from detecting product inconsistencies.

### 4.4 Regulatory Knowledge Base — ABSENT
No `regulatory_references.json` file exists. The taxonomy has hazard levels but no regulatory source (FSSAI, EFSA, FDA, Codex Alimentarius), no permitted-use conditions, no ADI (Acceptable Daily Intake) values with citations.

### 4.5 Separate Confidence Values — ABSENT
The spec requires four independent confidence values:
- OCR confidence (not collected from Tesseract)
- INS/additive matching confidence (partially proxied)
- Product identity confidence (absent)
- Barcode decoding confidence (absent — no image decode)

### 4.6 Product Verification Result Panel — ABSENT
The frontend has no UI for showing a multimodal verification result (Consistent / Mismatch / Insufficient / Needs Review). The dashboard shows score, additives, and counterfactual — but not whether the scanned product matches its barcode record.

### 4.7 Reviewer Correction Interface — ABSENT
The audit modal shows pending records but offers no interaction — no confirm button, no reject button, no text correction field, no status update.

### 4.8 Trained ML Model — ABSENT
`requirements.txt` lists `scikit-learn`, `xgboost`, and `shap`, but none of these are imported anywhere in the actual code. The import attempt for `shap` is wrapped in a try/except that silently falls back:
```python
try:
    import shap
    _HAS_SHAP = True
except ImportError:
    _HAS_SHAP = False  # Never used — fallback runs the same hardcoded rules
```
There is no trained model file (`.pkl`, `.json`, `.ubj`), no training script, no evaluation report.

### 4.9 Mobile-Responsive Layout — PARTIALLY ABSENT
The glassmorphism CSS uses fixed pixel widths and grid layouts that partially break on narrow screens. No explicit responsive breakpoints are defined in `style.css`.

---

## 5. Technical Weaknesses

### 5.1 SHAP Terminology Misuse (Critical)
The project calls fixed rule-based deductions "Shapley values" and "SHAP attributions." Shapley values are a game-theoretic concept defined relative to a trained predictive model. Using the term without a model is technically incorrect and would not withstand academic review.
**Risk:** Supervisor or examiner rejection of the research contribution.

### 5.2 Hardcoded Additive Penalties Without Cited Evidence
The deduction values (INS 250 → −18.5 pts, etc.) are not traced to any scientific source. Different additives receive arbitrary penalties that do not correspond to any recognised regulatory risk classification system (FSSAI, EFSA, etc.).

### 5.3 Taxonomy Has No Provenance
The `ins_taxonomy.json` file has no `source` field. The `hazard_weight` values (0.1 to 0.9) have no documented derivation. This means the entire scoring system's factual basis is unverifiable.

### 5.4 Barcode Implementation Misrepresented
The README says "barcode detection and decoding." The actual implementation is a text input field and a checksum function. A user must manually type the barcode number.

### 5.5 Confidence Values Are Circular
The "parser confidence" is computed as matched tokens / total tokens. High confidence means "most detected additives were in our taxonomy" — not that the OCR read correctly or that the product was correctly identified. A product with zero additives gets confidence 0.95 by default.

### 5.6 Taxonomy Tripled Storage (Space Inefficiency)
Each additive is stored under three keys: `"100"`, `"INS 100"`, and `"E100"` — all containing identical JSON objects. The 313 KB file stores ~3× more data than necessary. This does not affect correctness but wastes memory on load.

### 5.7 `requirements.txt` vs. Actual Imports
`requirements.txt` lists `requests`, `numpy`, `pandas`, `scikit-learn`, `xgboost`, `shap`. None of these are actually imported in the current code (barcode.py uses `urllib.request` explicitly to avoid `requests`). The file creates a false impression of ML usage.

### 5.8 No Input Validation on `/api/v1/analyze`
The endpoint accepts arbitrary JSON without validating field types, lengths, or data formats beyond what Python dict `.get()` provides. A missing `ean` field with a non-string `text` value can cause silent failures.

### 5.9 Audit Log Grows Unbounded
`unmapped_additives.json` is appended on every analysis that flags tokens. Running the test suite adds duplicate `INS 9999_UNKNOWN` entries each time. There is no deduplication, rotation, or size limit.

### 5.10 OCR Confidence Discarded
Tesseract.js provides word-level confidence (`res.data.words[].confidence`, 0–100). `App.js` only uses `res.data.text`, discarding all confidence metadata before the text is sent to the backend.

---

## 6. Research Limitations

### 6.1 No Real Trained Model
The core research contribution — "Explainable ML" — has no ML component. A rule-based system can be a valid research contribution, but it must be clearly described as such and compared against an ML baseline.

### 6.2 No Evaluation Metrics
There is no Character Error Rate (CER) or Word Error Rate (WER) measurement for OCR. There is no Precision/Recall/F1 for INS extraction. There is no evaluation of the scoring system against any ground-truth dataset.

### 6.3 No Real-World Test Images
The 4 benchmark products use fabricated ingredient text strings. There is no dataset of actual food packaging images with verified ground-truth barcodes, ingredient text, and additive labels.

### 6.4 Counterfactual Lacks Scientific Justification
The statement "removing INS 250 increases safety score from 62.5 to 81.0" is internally consistent (rule re-applied after removing the additive) but scientifically meaningless without evidence that removing sodium nitrite from a product actually produces a 29.6% improvement in consumer safety.

### 6.5 Mismatch Detection Research Gap Not Addressed
The main research question ("Can combining barcode + OCR information improve consistency detection?") is not implemented. No comparison baseline (barcode-only, OCR-only, combined) exists.

### 6.6 No Literature Verification
The README claims this addresses "Research Gap G2" and "Research Gap G3" without citing papers that establish these gaps exist.

---

## 7. Recommended Implementation Plan (Stage-by-Stage)

### Stage 2 — Corrections First (Before New Features)
**Priority: Fix what is wrong before building on top of it.**
1. Rename `ShapAttributionChart` → `RuleAttributionChart`. Relabel "SHAP" as "Rule-Based Indicator" throughout UI and backend. Add disclaimer text.
2. Rename scoring engine function to `compute_rule_based_score_and_attributions`. Remove misleading SHAP docstring.
3. Add `source`, `last_verified`, `verified` fields to taxonomy (can be null initially — marks unknowns).
4. Create `regulatory_references.json` skeleton with FSSAI/EFSA/Codex structure.
5. Forward Tesseract.js word-level confidence to the backend.
6. Fix audit log deduplication.
7. Add basic input validation to `/api/v1/analyze`.
8. Separate the four confidence values in the API response.

### Stage 3 — Barcode Image Intelligence
1. Add `pyzbar` + `Pillow` to requirements (barcode decoding from image, no YOLO needed initially).
2. Create `backend/services/barcode_decoder.py` — accepts image bytes, attempts pyzbar decode, returns `{barcode, confidence, method}`.
3. Add `/api/v1/barcode/decode` endpoint accepting base64 image.
4. Add frontend `BarcodeImageScanner` component to upload or capture → decode → display.
5. If pyzbar decode rate is insufficient for low-quality images, research YOLO localisation as a pre-processing step.
6. Test with real product images.

### Stage 4 — OCR Improvements
1. Send `ocr_confidence` (from Tesseract word scores, mean) with every analysis request.
2. Improve `parser.py` false positive filtering — currently `E` followed by digits anywhere in text matches E-numbers (e.g. "E100" in product codes, expiry dates "E2026").
3. Add ingredient boundary detection — extract only the ingredient list section, not the entire label.
4. Expand chemical name dictionary from 20 → 100+ common names.

### Stage 5 — Multimodal Verification (Core Research)
1. Create `backend/services/product_matcher.py`.
   - Input: `off_ingredients_text` (from barcode lookup), `ocr_ingredients_text` (from scan).
   - Compute ingredient overlap score (token-level Jaccard similarity).
   - Compute additive list comparison.
   - Classify: Consistent / Mismatch / Insufficient / Needs Review.
2. Add `verification_result` to API response schema.
3. Add `VerificationResultCard` React component.
4. This directly addresses the main research question.

### Stage 6 — Anomaly Detection and Reviewer UI
1. Create `backend/services/anomaly_detector.py` — rule-based baseline.
   - Signals: ingredient text mismatch > threshold, barcode lookup failure, name mismatch, zero ingredients from OCR.
2. Add reviewer actions to `AuditQueueModal` — Confirm / Reject / Correct buttons, status update API.
3. Create `/api/v1/audit/<id>/review` endpoint.

### Stage 7 — Research Evaluation
1. Collect 20–50 real food packaging images with known barcodes.
2. Manually annotate OCR ground truth and additive ground truth.
3. Compute CER, WER, INS Precision/Recall/F1.
4. Run three baselines: barcode-only, OCR-only, combined.
5. Document results in `EVALUATION.md`.

### Stage 8 — Finalisation
1. Full test suite update.
2. README rewrite with honest description.
3. Setup documentation.

---

## 8. Files That Need Modification

| File | Change Required | Priority |
|---|---|---|
| `backend/services/scoring_engine.py` | Remove SHAP terminology; rename to rule-based; add disclaimer field to output | HIGH |
| `backend/services/parser.py` | Fix false positive E-number matching; forward OCR confidence; expand name dict | HIGH |
| `backend/services/audit.py` | Add deduplication; add reviewer status update function; add separate confidence fields | HIGH |
| `backend/data/ins_taxonomy.json` | Add `source`, `last_verified`, `verified` fields per entry | MEDIUM |
| `backend/app.py` | Add input validation; add new endpoints for barcode decode and reviewer actions | HIGH |
| `backend/requirements.txt` | Add `pyzbar`, `Pillow`; remove unused entries (or keep but document honestly) | MEDIUM |
| `frontend/src/App.js` | Forward Tesseract confidence; add verification result rendering; add OCR confidence display | HIGH |
| `frontend/src/api.js` | Add `decodeBarcode()`, `submitReview()` functions | MEDIUM |
| `frontend/src/components/ShapAttributionChart.jsx` | Rename and relabel to remove SHAP claim | HIGH |
| `frontend/src/components/SafetyScoreCard.jsx` | Add disclaimer; rename "XAI Scoring" to "Rule-Based Indicator" | HIGH |
| `frontend/src/components/AuditQueueModal.jsx` | Add confirm/reject/correct buttons and API calls | MEDIUM |
| `frontend/src/style.css` | Add responsive breakpoints for mobile | LOW |

---

## 9. New Files That Need to Be Created

| File | Purpose | Stage |
|---|---|---|
| `backend/services/barcode_decoder.py` | Image-based barcode decoding using pyzbar/Pillow | Stage 3 |
| `backend/services/product_matcher.py` | Multimodal verification: compare OFF data vs. OCR data | Stage 5 |
| `backend/services/confidence_engine.py` | Combine separate confidence values with documented method | Stage 5 |
| `backend/services/anomaly_detector.py` | Rule-based anomaly signals; ML model hook | Stage 6 |
| `backend/services/regulatory_checker.py` | Look up regulatory references from JSON | Stage 2 |
| `backend/data/regulatory_references.json` | FSSAI/EFSA/Codex references per additive | Stage 2 |
| `frontend/src/components/VerificationResultCard.jsx` | Multimodal consistency result display | Stage 5 |
| `frontend/src/components/BarcodeImageScanner.jsx` | Upload/capture → image-based barcode decode | Stage 3 |
| `frontend/src/components/ConfidencePanel.jsx` | Show all four confidence values separately | Stage 2 |
| `tests/test_barcode_decoder.py` | Tests for image-based barcode decoding | Stage 3 |
| `tests/test_product_matcher.py` | Tests for multimodal verification | Stage 5 |
| `tests/test_anomaly_detector.py` | Tests for anomaly detection | Stage 6 |
| `EVALUATION.md` | Dataset, metrics, baseline comparison results | Stage 7 |
| `DATA_COLLECTION_PLAN.md` | Plan for acquiring real food packaging images | Stage 7 |

---

## 10. Summary Table

| Dimension | Current State | Target for SafeBite 2.0 |
|---|---|---|
| Barcode input | Manual text entry | Image-based detection + decode |
| Scoring | Rule-based (mislabelled SHAP) | Clearly rule-based; ML planned |
| Confidence | 1 misleading value | 4 separate values |
| Multimodal verification | Not implemented | Core feature |
| Anomaly detection | Not implemented | Rule-based baseline |
| Taxonomy provenance | None | Source + verification status |
| Regulatory knowledge | Not present | Structured references JSON |
| Reviewer interface | Read-only modal | Confirm/reject/correct |
| Tests | 8 (all pass) | 20+ covering new modules |
| Research evaluation | None | CER, WER, P/R/F1, baselines |
| OCR confidence | Discarded | Forwarded and displayed |

---

## 11. What Is Genuinely Strong in the Existing Project

> These should be preserved and built on — not rewritten.

- ✅ EAN-13 validation — correct and well-tested.
- ✅ Open Food Facts API connector — works, has fallback, salt→sodium conversion.
- ✅ Taxonomy file — 750+ entries, good coverage, usable structure (needs provenance).
- ✅ Regex OCR normaliser — technically sound, handles common Tesseract errors.
- ✅ Flask architecture — clean route separation, CORS working, logging in place.
- ✅ React component structure — modular, each component has a single responsibility.
- ✅ Glassmorphism UI — professional appearance, dark theme, responsive gauges.
- ✅ Audit log — JSON append works, correct timestamps, useful for future use.
- ✅ Tesseract.js integration — in-browser, avoids server-side OCR dependency.
- ✅ Test suite structure — well-organised, easy to extend.

---

*Stage 1 complete. Awaiting approval to proceed to Stage 2.*
