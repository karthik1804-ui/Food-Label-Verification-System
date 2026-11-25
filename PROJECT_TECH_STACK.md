# Food Label Verification System — Technology Stack Reference

This document provides a verified inventory of all programming languages, frameworks, runtime libraries, external APIs, and developer tools used in the **Food Label Verification System**.

All entries are verified directly against `backend/requirements.txt`, `frontend/package.json`, database configurations, and active source code imports.

---

## 1. Programming Languages & Runtimes

| Category | Technology | Version | Actual Purpose in Codebase | Implementation Status |
|---|---|---|---|---|
| Language | Python | 3.10+ (Verified on 3.14) | Core backend language powering the REST API server, image processing pipelines, INS parsing, scoring engines, database access, and test suites. | Fully Verified |
| Language | JavaScript (ES6+ / JSX) | ECMAScript 2022+ | Frontend development language powering the React UI, interactive modals, camera streaming, and client-side OCR. | Fully Verified |
| Runtime | Node.js & npm | Node 18+ / npm 9+ | Build environment and package manager for the React single-page application. | Fully Verified |
| Runtime | CPython / SQLite Engine | Embedded C runtime | Executes SQLite database transactions, enforcing relational foreign keys and indices. | Fully Verified |

---

## 2. Backend Frameworks & Core Libraries

| Category | Technology | Specification / Version | Actual Purpose in Codebase | Implementation Status |
|---|---|---|---|---|
| Web Framework | Flask | `>=3.0.0` (Installed 3.1.3) | Lightweight WSGI web framework providing HTTP routing, JSON request/response parsing, error handlers, and CORS integration. | Fully Verified |
| Cross-Origin | Flask-CORS | `>=4.0.0` (Installed 6.0.2) | Handles Cross-Origin Resource Sharing (CORS) headers for communication with React on `localhost:3000`. | Fully Verified |
| Security / Crypto | Werkzeug | `>=3.0.0` (Installed 3.1.8) | Generates salted PBKDF2:SHA256 password hashes (`generate_password_hash`) and validates authentication passwords (`check_password_hash`). | Fully Verified |
| HTTP Client | Requests / urllib | Requests `>=2.31.0` / standard `urllib.request` | Communicates with the external Open Food Facts REST API to fetch product metadata and nutritional facts. | Fully Verified |
| Environment | python-dotenv | `>=1.0.0` (Installed 1.2.2) | Loads environment variables (`DATABASE_PATH`, `JWT_SECRET`, port configs) from `.env` files. | Fully Verified |

---

## 3. Computer Vision & Optical Character Recognition (OCR)

| Category | Technology | Specification / Version | Actual Purpose in Codebase | Implementation Status |
|---|---|---|---|---|
| Computer Vision | OpenCV (`opencv-python`) | `>=4.8.0` (Installed 4.13.0) | High-performance image processing: aspect-ratio resizing, bilateral filtering, CLAHE contrast enhancement, unsharp-mask sharpening, Otsu thresholding, Laplacian blur estimation, and 1D barcode decoding (`cv2.barcode.BarcodeDetector`). | Fully Verified |
| Client-Side OCR | Tesseract.js | `^5.0.0` (in `package.json`) | WebAssembly port of Tesseract OCR running in the user's browser. Extracts text from package photos and generates word-level confidence metrics. | Fully Verified |
| Numerical Arrays | NumPy | `>=1.24.0` (Installed 2.4.5) | Low-level matrix representation of image pixel buffers for OpenCV transformations and mathematical operations. | Fully Verified |

---

## 4. Frontend Frameworks & UI Libraries

| Category | Technology | Specification / Version | Actual Purpose in Codebase | Implementation Status |
|---|---|---|---|---|
| UI Framework | React | `^18.2.0` | Declarative component architecture for managing state, view routing, modals, form inputs, and live scan streams. | Fully Verified |
| DOM Renderer | React-DOM | `^18.2.0` | Mounts and reconciles the React virtual DOM tree into the browser document. | Fully Verified |
| Build Tooling | Create React App (`react-scripts`) | `5.0.1` | Webpack, Babel, and development server tooling for compiling JSX and bundling production assets. | Fully Verified |
| HTTP Client | Axios | `^1.6.0` | Promise-based HTTP client for browser API requests. Includes automatic retry logic from `localhost:5005` to `127.0.0.1:5005`. | Fully Verified |
| Icons | Lucide React | `^0.300.0` | Minimalist SVG icons for UI navigation, badges, warning states, and buttons. | Fully Verified |
| Hardware Video | React-Webcam | `^7.2.0` | React wrapper accessing user camera devices via `navigator.mediaDevices.getUserMedia` for real-time label and barcode capture. | Fully Verified |
| Data Charts | Recharts | `^2.10.0` | Declarative SVG charting library used to render score deduction breakdowns and audit metrics. | Fully Verified |

---

## 5. Database & Persistence Layer

| Category | Technology | Specification / Version | Actual Purpose in Codebase | Implementation Status |
|---|---|---|---|---|
| Database Engine | SQLite | SQLite 3 | Serverless, zero-configuration relational database stored locally at `backend/data/app.db`. | Fully Verified |
| Relational Schema | Native SQL DDL | SQLite 3 syntax | Manages relational tables: `users`, `auth_tokens`, `dietary_profiles`, and `analysis_history` with foreign key cascade actions. | Fully Verified |
| File Storage | Flat JSON Files | JSON (UTF-8) | Stores static knowledge bases: `ins_taxonomy.json` (750 entries), `regulatory_references.json` (22 entries), and dynamic audit log `unmapped_additives.json`. | Fully Verified |

---

## 6. External APIs & Data Sources

| API / Data Source | Provider | Access Mode | Actual Usage in System | Status |
|---|---|---|---|---|
| Open Food Facts API | Open Food Facts | Public REST API (`https://world.openfoodfacts.org/api/v2/`) | Fetches product brand, name, categories, ingredients text, and macronutrients based on scanned EAN-13 barcode. | Fully Verified |
| Offline Benchmark Catalog | Local Mock | In-memory dictionary (`BENCHMARK_PRODUCTS`) | 4 pre-configured packaged food products used when Open Food Facts is offline or unreachable. | Fully Verified |
| INS Additive Taxonomy | Local Authority | Static JSON dataset | 750 food additives mapped to canonical names, functional classes, synonyms, and hazard classifications based on Codex Alimentarius / FSSAI. | Fully Verified |
| Regulatory Database | Local Authority | Static JSON dataset | 22 comprehensive regulatory profiles detailing FSSAI, EFSA, Codex, and FDA safety statuses and ADI values. | Fully Verified |

---

## 7. Testing & Quality Assurance Infrastructure

| Category | Technology | Actual Purpose in Codebase | Implementation Status |
|---|---|---|---|
| Test Runner | Python `unittest` | Native standard library test runner executing test suites across 12 test files. | Fully Verified (187 passing tests) |
| Test Framework | Pytest / Pytest-Cov | Configuration present; automated test suite fully compatible with both `pytest` and `unittest`. | Fully Verified |
| Regression Test Suite | `tests/test_regression_coderabbit.py` | Automated validation of memory bounds, payload sanitization, and fallback safety. | Fully Verified |
| End-to-End Test Suite | `tests/test_full_system.py` | Integration test exercising end-to-end user registration, profile setup, image preprocessing, parsing, scoring, and history retrieval. | Fully Verified |
