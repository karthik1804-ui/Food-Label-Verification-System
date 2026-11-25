"""
chapter_5.py
Chapter 5: SYSTEM IMPLEMENTATION
Comprehensive technical documentation of algorithms, OpenCV pipeline stages,
Tesseract integration, INS taxonomy (750 entries), preference engine, scoring formulas,
confidence vector, HITL audit queue, REST API endpoints, and authentic UI screenshots.
"""

from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def build_chapter_5(builder):
    builder.add_chapter_title("5", "SYSTEM IMPLEMENTATION")

    # 5.1 Development Environment
    builder.add_h1("5.1 Development Environment Setup and Configuration")
    builder.add_p(
        "The Food Label Verification System was engineered across an isolated full-stack development environment designed for high "
        "reproducibility and cross-platform compatibility. The backend service layer is implemented in Python 3.14.0 on Windows and Linux "
        "operating systems. Core computational dependencies—including OpenCV (version 4.13.0.92), Tesseract OCR (version 5.0.0), and "
        "NumPy (version 2.4.5)—were installed in an isolated virtual environment. The frontend client application was developed using "
        "Node.js (v20 LTS), npm (v10), and React 18.3.1."
    )

    # 5.2 Full-Stack Overview
    builder.add_h1("5.2 Full-Stack Implementation Overview")
    builder.add_p(
        "The system implementation adheres to clean separation of concerns across a modern decoupled architecture. The backend is "
        "structured into three primary packages: `backend/models/` manages SQLite database connections, entity schemas, and table definitions; "
        "`backend/services/` contains specialized domain logic modules for barcode decoding, image preprocessing, optical recognition, "
        "taxonomy resolution, dietary scoring, and audit logging; and `backend/data/` houses the authoritative static JSON knowledgebases "
        "(`ins_taxonomy.json` and `regulatory_references.json`). The Flask gateway (`backend/app.py`) coordinates request routing, "
        "enforcing strict input validation and CORS policies across 31 verified REST endpoints."
    )

    # Table 5.1: REST API Routes
    headers_t51 = ["HTTP Method", "Endpoint Path", "Controller Function", "Operational Purpose"]
    data_t51 = [
        ["POST", "/api/v1/analyze", "analyze()", "Primary multimodal analysis (Pipeline A + Pipeline B)."],
        ["POST", "/api/v1/barcode/decode", "decode_barcode()", "Detects and decodes EAN-13 barcode from image bytes."],
        ["GET", "/api/v1/product/<barcode>", "get_product_by_barcode()", "Retrieves product metadata from Open Food Facts / cache."],
        ["POST", "/api/v1/auth/register", "register()", "Registers new user with PBKDF2 hashed password."],
        ["POST", "/api/v1/auth/login", "login()", "Authenticates user and issues 64-char session token."],
        ["POST", "/api/v1/auth/logout", "logout()", "Revokes and deletes active session token from SQLite."],
        ["GET", "/api/v1/auth/me", "get_current_user()", "Returns authenticated profile for active session token."],
        ["GET / PUT", "/api/v1/profile", "manage_profile()", "Retrieves or updates active user dietary preferences."],
        ["GET", "/api/v1/profile/presets", "get_presets()", "Returns available lifestyle presets and default configurations."],
        ["POST", "/api/v1/profile/allergies", "update_allergies()", "Updates user's selected allergen list."],
        ["POST", "/api/v1/ocr/preprocess", "preprocess_image()", "Executes OpenCV Configuration B enhancement on uploaded image."],
        ["POST", "/api/v1/ocr/compare", "compare_ocr()", "Executes live benchmark comparing Config A vs Config B."],
        ["GET", "/api/v1/audit/unmapped", "get_unmapped_audit()", "Retrieves pending unmapped additive review queue."],
        ["POST", "/api/v1/audit/<id>/review", "review_audit()", "Executes auditor action (confirm, correct, reject)."],
        ["GET", "/api/v1/history", "get_history()", "Returns paginated scan history with search and verdict filters."],
        ["GET", "/api/v1/history/export", "export_history()", "Exports scan history in JSON or CSV format."]
    ]
    builder.add_table("Table 5.1: Implemented REST API Route Catalog and Endpoint Specifications", headers_t51, data_t51,
                      col_widths=[Inches(1.1), Inches(2.3), Inches(1.8), Inches(2.0)])

    # 5.3 Authentication
    builder.add_h1("5.3 Authentication, Token Management, and PBKDF2 Password Hashing")
    builder.add_p(
        "User security and credential protection are implemented in `backend/services/auth_service.py`. When a user registers via "
        "`/api/v1/auth/register`, the service validates that the username and email are unique, enforces a minimum password length of "
        "8 characters, and generates a cryptographically secure random 16-byte salt using `os.urandom(16)`. Passwords are hashed using "
        "the Password-Based Key Derivation Function 2 (PBKDF2) with the HMAC-SHA256 pseudo-random function, executed for exactly "
        "100,000 iterations to resist brute-force dictionary attacks."
    )
    builder.add_p(
        "Upon successful authentication, the server generates a 64-character hexadecimal session token using `secrets.token_hex(32)`. "
        "The token is stored in the `auth_tokens` table with an explicit expiration timestamp set to 7 days ($604,800$ seconds) from issuance. "
        "Subsequent client requests include this bearer token in the `Authorization` header (`Bearer <token>`). The authentication middleware "
        "validates token existence, verifies that `expires_at > CURRENT_TIMESTAMP`, and injects the corresponding user entity into request context."
    )

    # Insert Figure 5.1
    builder.add_figure("Figure 5.1: User Authentication and Registration Interface (Authentic UI)", "fig_5_1_ui_auth.png", width_inches=4.0)

    # 5.4 Barcode Decoding and Modulo-10 Checksum Algorithm
    builder.add_h1("5.4 Barcode Decoding and Modulo-10 Checksum Algorithm Implementation")
    builder.add_p(
        "Barcode decoding and validation are implemented in `backend/services/barcode.py`. The barcode detection module ingests "
        "image bytes, decodes the frame via PyZbar/ZXing, and extracts the raw string. To verify mathematical integrity before querying "
        "external networks, the service executes `validate_ean13(barcode: str) -> bool` using the international Modulo-10 checksum algorithm."
    )
    builder.add_p(
        "The mathematical formulation of the Modulo-10 check digit verification is defined as:\n\n"
        "Let the 13-digit EAN sequence be represented as $D = [d_0, d_1, d_2, \\dots, d_{12}]$, where $d_0$ to $d_{11}$ constitute the "
        "data payload and $d_{12}$ represents the transmitted check digit.\n\n"
        "1. Sum the digits at even indices (0-indexed, representing odd positions):\n"
        "$$S_{\\text{odd}} = \\sum_{i \\in \\{0, 2, 4, 6, 8, 10\\}} d_i$$\n\n"
        "2. Sum the digits at odd indices (0-indexed, representing even positions) and multiply by 3:\n"
        "$$S_{\\text{even}} = 3 \\times \\sum_{i \\in \\{1, 3, 5, 7, 9, 11\\}} d_i$$\n\n"
        "3. Compute the combined total and derive the check digit:\n"
        "$$T = S_{\\text{odd}} + S_{\\text{even}}$$\n"
        "$$C = (10 - (T \\pmod{10})) \\pmod{10}$$\n\n"
        "The barcode is mathematically valid if and only if $C = d_{12}$. If the string length is not 13, contains non-numeric characters, "
        "or fails the check digit equality, the function returns `False`, terminating external database queries."
    )

    # 5.5 Open Food Facts Integration with Offline Fallback
    builder.add_h1("5.5 Open Food Facts Integration with Offline Benchmark Fallback")
    builder.add_p(
        "Following successful Modulo-10 verification, `fetch_product_by_barcode(barcode: str)` queries the Open Food Facts API v0. "
        "To ensure robust error handling under unstable retail network connectivity, the request is wrapped in a strict 4.0-second socket "
        "timeout guard using `urllib.request.urlopen(req, timeout=4.0)`. The service inspects the JSON response for `status == 1` and "
        "extracts product names, brands, categories, ingredients text, and nutriments (sugars, sodium, saturated fat per 100g)."
    )
    builder.add_p(
        "If a network timeout occurs, HTTP resolution fails (`urllib.error.URLError`), or the product is unlisted, the service queries an "
        "internal `BENCHMARK_PRODUCTS` dictionary populated with curated reference items (e.g., `8901234567890` for processed snack items, "
        "`8901030000003` for salty crisps, `5449000000996` for carbonated cola, and `8901725132224` for instant noodles). This guarantees "
        "complete offline resilience during academic presentations and benchmark testing."
    )

    # 5.6 OpenCV Preprocessing Pipeline (Bilateral Filter, CLAHE, Sharpness)
    builder.add_h1("5.6 OpenCV Preprocessing Pipeline (Bilateral Filter, CLAHE, Sharpness)")
    builder.add_p(
        "The computer vision enhancement pipeline is implemented in `backend/services/ocr/image_preprocessor.py` under the "
        "`ImagePreprocessor` class. The pipeline executes eight distinct algorithmic operations designed specifically to stabilize "
        "food packaging imagery before OCR ingestion:\n\n"
        "1. Format Validation and Memory Ceilings: Image bytes are validated to reject empty buffers or corrupt headers. Decoded dimensions "
        "are strictly bounded: $w \\times h \\le 25,000,000$ pixels (25 MP safety ceiling) and maximum dimension $\\le 4096\\text{px}$ to "
        "prevent decompression bomb memory exhaustion.\n\n"
        "2. Laplacian Sharpness Assessment: The service converts the image to grayscale and computes the discrete Laplacian operator using "
        "a $3 \\times 3$ kernel via `cv2.Laplacian(gray, cv2.CV_64F)`. The optical blur score is defined as the statistical variance:\n"
        "$$\\text{Blur Score} = \\sigma^2_{\\text{Lap}} = \\frac{1}{N} \\sum_{x,y} (L(x,y) - \\mu_L)^2$$\n"
        "If $\\sigma^2_{\\text{Lap}} < 70.0$, the image is flagged as blurry, directing downstream modules to avoid aggressive unsharp masking.\n\n"
        "3. Illumination Uniformity Assessment: The image is divided into four equal quadrants ($Q_1, Q_2, Q_3, Q_4$). The mean intensity "
        "$\\mu_k$ of each quadrant is calculated. If the standard deviation across quadrant means $\\sigma_{\\text{quad}} > 35.0$, the image "
        "is flagged for adaptive binarization.\n\n"
        "4. Aspect-Ratio Rescaling: For packaging with microscopic fonts, images with dimensions below $1200 \\times 900$ pixels are scaled "
        "up to $3.0\\times$ using bicubic interpolation (`cv2.INTER_CUBIC`), capped at the 4096 px dimension boundary.\n\n"
        "5. Bilateral Edge-Preserving Denoising: Surface noise and printing artifacts are smoothed while preserving crisp character boundaries "
        "by applying `cv2.bilateralFilter(gray, d=5, sigmaColor=35, sigmaSpace=35)`.\n\n"
        "6. Contrast-Limited Adaptive Histogram Equalization (CLAHE): Applied with `clipLimit=2.2` and tile grid $(8, 8)$, redistributing "
        "local luminance to eliminate specular highlights on glossy plastic.\n\n"
        "7. Controlled Unsharp Masking: The contrast-enhanced frame is blurred via a Gaussian kernel ($\\sigma=2.5$). A sharpened frame is "
        "synthesized via `cv2.addWeighted(contrast_enhanced, 1.35, blurred, -0.35, 0)`.\n\n"
        "8. Adaptive Gaussian Binarization: If uneven lighting was flagged in Step 3, the pipeline computes an adaptive binary frame using "
        "`cv2.adaptiveThreshold(contrast_enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 10)`."
    )

    # 5.7 Dual-Configuration OCR Engine and Tesseract Integration
    builder.add_h1("5.7 Dual-Configuration OCR Engine and Tesseract Integration")
    builder.add_p(
        "Orchestrated by `backend/services/ocr/ocr_pipeline.py` and `backend/services/ocr_service.py`, the optical engine coordinates "
        "between Configuration A (Baseline Tesseract on raw image) and Configuration B (Tesseract on preprocessed candidate). "
        "Both configurations execute Tesseract 5.0 with identical core parameters: English language pack (`-l eng`), Page Segmentation Mode 6 "
        "(`--psm 6`, assuming a single uniform block of text), and inter-word space preservation (`-c preserve_interword_spaces=1`)."
    )
    builder.add_p(
        "Tesseract word-level confidence values are extracted from the TSV output matrix. Confidence scores corresponding to whitespace "
        "or single punctuation tokens are discarded, and the arithmetic mean across alphanumeric word tokens is calculated to produce the "
        "normalized OCR confidence metric $C_{\\text{ocr}} \\in [0.0, 1.0]$. If Configuration B preprocessing encounters an unexpected "
        "exception, the pipeline catches the error, logs a warning, and automatically executes Configuration A."
    )

    # 5.8 Token Normalization, Typo Correction, and Regex Extraction
    builder.add_h1("5.8 Token Normalization, Typo Correction, and Regex Extraction")
    builder.add_p(
        "Extracted raw text undergoes domain-specific lexical normalization in `backend/services/parser.py`. A common failure mode in "
        "packaging OCR is the visual confusion of alphanumeric characters (e.g., numeral '1' misread as capital 'I' or lower-case 'l'; "
        "numeral '0' misread as capital 'O' or 'o'). Applying global string replacement across the entire text stream corrupts valid words "
        "(e.g., turning 'OIL' into '011'). To resolve this, `normalize_ocr_errors(text: str)` employs targeted regular expressions that "
        "restrict typo substitution strictly to INS and E-number token prefixes:"
    )
    builder.add_p(
        "```python\n"
        "# Pass 1: Correct 1NS / 1N5 / IN5 typographical misreads\n"
        "text = re.sub(r'\\b1NS\\b', 'INS', text, flags=re.IGNORECASE)\n"
        "text = re.sub(r'\\b1N5\\b', 'INS', text, flags=re.IGNORECASE)\n\n"
        "# Pass 2: Substitute visual confusions strictly within numerical INS body\n"
        "def clean_ins_match(match):\n"
        "    prefix, body = match.group(1), match.group(2)\n"
        "    cleaned = (body.replace('I', '1').replace('l', '1')\n"
        "                   .replace('O', '0').replace('o', '0'))\n"
        "    return f'{prefix}{cleaned}'\n\n"
        "text = re.sub(r'(\\bINS\\s*[:\\-]?\\s*)([0-9IlOo]{2,4}[a-zA-Z]?(?:\\([ivxIVX1-9]+\\))?)',\n"
        "              clean_ins_match, text, flags=re.IGNORECASE)\n"
        "```"
    )
    builder.add_p(
        "Following typo correction, `extract_additive_tokens(text: str)` extracts additive candidates using four complementary patterns:\n\n"
        "1. Standard INS tokens: `\\bINS\\s*[:\\-]?\\s*(\\d{2,4}[a-zA-Z]?(?:\\([ivxIVX1-9]+\\))?)` (e.g., INS 250, INS:551, INS 500(i)).\n"
        "2. Codex-Validated E-numbers: Regex `\\bE\\s*[:\\-]?\\s*(\\d{2,4}[a-zA-Z]?)` coupled with a strict range validator asserting "
        "that $100 \\le \\text{code} \\le 1599$. Furthermore, lookbehind assertions prevent false positives on energy or mass units "
        "(e.g., `2000 kJ`, `10g`) and suppress 'VITAMIN E' from matching additive token E 306.\n"
        "3. Bracketed category expressions: Matches expressions such as 'permitted colours (102, 110)' or 'emulsifiers (322, 471)'.\n"
        "4. Canonical chemical synonym matching: Searches an indexed dictionary of 760+ chemical names (e.g., Monosodium Glutamate $\\rightarrow$ INS 621)."
    )

    # 5.9 INS Taxonomy Implementation (750 Curated Entries across 7 Classes)
    builder.add_h1("5.9 INS Taxonomy Implementation (750 Curated Entries across 7 Classes)")
    builder.add_p(
        "The system's knowledgebase is anchored in `backend/data/ins_taxonomy.json`, containing exactly **750 verified additive records**. "
        "Every record defines official substance nomenclature, hazard classifications, and functional classes. Table 5.2 documents the "
        "distribution of additives across the seven major functional series."
    )

    # Table 5.2: Taxonomy Distribution
    headers_t52 = ["INS Numeric Series", "Functional Category", "Substance Count", "Representative Examples", "Typical Concern"]
    data_t52 = [
        ["100 – 199", "Colors & Pigments", "94", "INS 100 (Curcumin), INS 102 (Tartrazine), INS 150d (Caramel IV)", "Hyperactivity in children; Southampton 6 azo dyes."],
        ["200 – 299", "Preservatives & Antimicrobials", "82", "INS 211 (Sodium Benzoate), INS 250 (Sodium Nitrite)", "IARC Group 2A nitrosamine carcinogens; asthmatic triggers."],
        ["300 – 399", "Antioxidants & Acidity Regulators", "116", "INS 320 (BHA), INS 321 (BHT), INS 330 (Citric Acid)", "IARC Group 2B possible carcinogens; endocrine disruption."],
        ["400 – 499", "Thickeners, Emulsifiers, Stabilizers", "168", "INS 407 (Carrageenan), INS 412 (Guar Gum), INS 471 (Glycerides)", "Gastrointestinal inflammation; hidden animal origins."],
        ["500 – 599", "pH Regulators & Anti-Caking Agents", "78", "INS 500(ii) (Baking Soda), INS 551 (Silicon Dioxide)", "Nanoparticle absorption concerns; generic parent ambiguity."],
        ["600 – 699", "Flavor Enhancers", "46", "INS 621 (Monosodium Glutamate), INS 627, INS 631", "Neurological excitotoxicity sensitivity; Chinese Restaurant Syndrome."],
        ["900 – 1599", "Sweeteners, Glazes, Gases, Modified Starches", "166", "INS 950 (Acesulfame K), INS 951 (Aspartame), INS 955 (Sucralose)", "IARC Group 2B carcinogen re-evaluation (2023); metabolic disruption."]
    ]
    builder.add_table("Table 5.2: INS Additive Functional Category Mapping in Curated Taxonomy", headers_t52, data_t52,
                      col_widths=[Inches(1.0), Inches(1.8), Inches(0.8), Inches(2.2), Inches(1.4)])

    # 5.10 Dietary Preference Evaluation and Lifestyle Presets
    builder.add_h1("5.10 Dietary Preference Evaluation and Lifestyle Preset Matching")
    builder.add_p(
        "Implemented in `backend/services/preference_engine.py`, the preference engine evaluates parsed additives and raw text "
        "against user-configured dietary profiles. The system provides four built-in lifestyle presets alongside custom granular toggles. "
        "Table 5.3 summarizes the preset rules."
    )

    # Table 5.3: Lifestyle Presets
    headers_t53 = ["Preset Name", "Target Demographic", "Avoidance Rule Configurations", "Default Penalty Profile"]
    data_t53 = [
        ["Clean Eating", "Health-conscious consumers avoiding synthetic chemicals", "Avoid synthetic colors, chemical preservatives, artificial sweeteners, and MSG.", "Deducts 15 pts per synthetic category match; flags all chemical additives."],
        ["Strict Vegan", "Ethical and plant-based vegan consumers", "Strictly avoids all animal-derived additives (INS 120, 428, 542, 901, 904, 920) and meat/dairy terms.", "Deducts 20 pts per animal-derived additive; flags non-vegan ingredients as CRITICAL."],
        ["Allergen Sensitive", "Consumers with celiac disease, nut allergies, or atopic sensitivity", "Enforces strict keyword matching across 11 major allergen categories; prioritizes safety.", "Deducts 50 pts per matched allergen; emits prominent, high-contrast warning banner."],
        ["Low Additive / Child Safe", "Parents and pediatric care providers", "Penalizes Southampton Six azo dyes and heavy chemical preservatives linked to hyperactivity.", "Deducts 15 pts per synthetic dye; highlights behavioral warning labels."]
    ]
    builder.add_table("Table 5.3: Dietary Lifestyle Presets and Default Avoidance Configurations", headers_t53, data_t53,
                      col_widths=[Inches(1.3), Inches(1.8), Inches(2.3), Inches(1.8)])

    # 5.11 Personalised Food Suitability Scoring Algorithm
    builder.add_h1("5.11 Personalised Food Suitability Scoring Algorithm (0-100 Deductions)")
    builder.add_p(
        "The Personalised Suitability Score is calculated deterministically via a transparent, rule-based mathematical deduction model. "
        "The system starts from an optimal baseline of 100 points and subtracts explicit penalties corresponding to profile conflicts:"
    )
    builder.add_p(
        "$$\\text{Personal Score} = \\max\\left(0, \\min\\left(100, 100 - \\sum_{k=1}^{M} P_k\\right)\\right)$$\n"
        "where $P_k$ represents the deduction penalty for the $k$-th detected rule violation, defined in Table 5.4."
    )

    # Table 5.4: Deduction Matrix
    headers_t54 = ["Rule Identifier", "Conflict Trigger", "Severity", "Deduction ($P_k$)", "Academic & Regulatory Rationale"]
    data_t54 = [
        ["RULE_CRITICAL_ALLERGEN", "Ingredient matches user's configured allergen list", "CRITICAL", "-50 Points", "Mandatory safety rule; protects sensitized consumers from anaphylaxis."],
        ["RULE_EXPLICIT_AVOID_INS", "Additive matches user's custom avoided INS code", "CRITICAL", "-20 Points", "Direct consumer preference violation; strictly penalizes chosen avoidance codes."],
        ["RULE_ANIMAL_DERIVATIVE", "Additive is animal-derived in Vegan profile", "CRITICAL", "-20 Points", "Ethical dietary violation (e.g., INS 120 Carmine, INS 428 Gelatin)."],
        ["RULE_SYNTHETIC_COLOR", "Synthetic dye detected in Clean Eating profile", "WARNING", "-15 Points", "Avoids artificial colors associated with pediatric behavioral hyperactivity."],
        ["RULE_AVOID_PRESERVATIVE", "Chemical preservative in Clean Eating profile", "WARNING", "-15 Points", "Penalizes antimicrobial chemical preservatives (e.g., benzoates, nitrites)."],
        ["RULE_AVOID_SWEETENER", "Artificial intense sweetener detected", "WARNING", "-15 Points", "Flags chemical sweeteners (aspartame, sucralose, acesulfame K)."],
        ["RULE_AVOID_MSG", "Monosodium Glutamate (INS 621) detected", "WARNING", "-15 Points", "Penalizes added flavor enhancers in MSG-restricted profiles."],
        ["RULE_CAUTION_INS", "Additive matches user's custom caution list", "CAUTION", "-10 Points", "Advisory deduction for substances user wishes to moderate."]
    ]
    builder.add_table("Table 5.4: Rule-Based Scoring Deduction Matrix and Hazard Weights", headers_t54, data_t54,
                      col_widths=[Inches(1.8), Inches(1.8), Inches(1.0), Inches(1.1), Inches(1.5)])

    builder.add_p(
        "Concurrently, the universal baseline safety score is computed independently in `scoring_engine.py` starting from Base Score 90.0, "
        "subtracting specific additive penalties (Table 5.5) and nutrient penalties based on World Health Organization (WHO) thresholds "
        "(e.g., sugars > 22.5g/100g: $-8.0$ pts; sodium > 1.5g/100g: $-10.0$ pts; saturated fat > 5.0g/100g: $-7.0$ pts)."
    )

    # Table 5.5: Specific Additive Regulatory Penalties
    headers_t55 = ["Additive Code", "Common Chemical Name", "Penalty Points", "Regulatory Authority & Toxicological Source"]
    data_t55 = [
        ["INS 250", "Sodium Nitrite", "-18.5 Points", "IARC Group 2A probable human carcinogen (nitrosamines in cured meats)."],
        ["INS 251", "Sodium Nitrate", "-16.0 Points", "IARC related; precursor to nitrite conversion in gastrointestinal tract."],
        ["INS 211", "Sodium Benzoate", "-12.0 Points", "EFSA Southampton replication concern; benzene formation with Vitamin C."],
        ["INS 320 / 321", "BHA / BHT", "-11.0 Points", "IARC Group 2B possible human carcinogen; endocrine disruption concerns."],
        ["INS 129", "Allura Red AC", "-10.5 Points", "Southampton Six azo dye; EFSA warning label mandatory in European Union."],
        ["INS 220", "Sulphur Dioxide", "-10.0 Points", "EU mandatory allergen declaration; acute bronchospasm trigger in asthmatics."],
        ["INS 102", "Tartrazine", "-9.5 Points", "Southampton Six colorant; EFSA reduced ADI to 7.5 mg/kg body weight/day."],
        ["INS 951", "Aspartame", "-8.5 Points", "IARC Group 2B possible carcinogen (2023 classification); intense sweetener."],
        ["INS 150d", "Caramel IV (Ammonia Sulphite)", "-8.0 Points", "California Proposition 65 listing; 4-methylimidazole (4-MEI) byproduct concern."],
        ["INS 621", "Monosodium Glutamate (MSG)", "-7.5 Points", "EFSA opinion: safe at normal use; acute sensitivity reported at high doses."]
    ]
    builder.add_table("Table 5.5: Specific Additive Regulatory Penalty Catalog", headers_t55, data_t55,
                      col_widths=[Inches(1.2), Inches(1.8), Inches(1.2), Inches(3.0)])

    # 5.12 Multimodal Confidence Vector Formulation
    builder.add_h1("5.12 Multimodal Confidence Vector Formulation")
    builder.add_p(
        "To guarantee auditability and prevent silent guessing, the system formulates a 4-dimensional confidence vector $\\vec{C}$ for "
        "every processed packaging item:\n\n"
        "$$\\vec{C} = \\left[ C_{\\text{ocr}},\\; C_{\\text{additive}},\\; S_{\\text{barcode}},\\; C_{\\text{identity}} \\right]$$\n\n"
        "where the vector components are formally defined in Table 5.6."
    )

    # Table 5.6: Confidence Vector
    headers_t56 = ["Component", "Symbol", "Domain / Type", "Derivation Mathematical Formulation"]
    data_t56 = [
        ["OCR Text Confidence", "$C_{\\text{ocr}}$", "Float $[0.0, 1.0]$", "Arithmetic mean of word-level Tesseract confidence scores: $\\frac{1}{K} \\sum c_k$."],
        ["Additive Match Confidence", "$C_{\\text{additive}}$", "Float $[0.0, 1.0]$", "Ratio of mapped tokens to total extracted candidate strings: $N_{\\text{mapped}} / N_{\\text{total}}$."],
        ["Barcode Decode Status", "$S_{\\text{barcode}}$", "String Enum", "Discrete outcome: `valid_ean13`, `invalid_checksum`, `not_provided`, `lookup_failed`."],
        ["Product Identity Certainty", "$C_{\\text{identity}}$", "Float $[0.0, 1.0]$", "1.0 if valid EAN + found in OFF; 0.5 if no barcode provided; 0.0 if lookup failed."]
    ]
    builder.add_table("Table 5.6: Multimodal Confidence Vector Component Definitions", headers_t56, data_t56,
                      col_widths=[Inches(1.8), Inches(1.0), Inches(1.5), Inches(2.9)])

    # 5.13 Regulatory Reference Cross-Checking Module
    builder.add_h1("5.13 Regulatory Reference Cross-Checking Module (FSSAI, EFSA, Codex)")
    builder.add_p(
        "Implemented in `backend/services/regulatory_checker.py`, this module cross-references detected additives against official "
        "statutes stored in `backend/data/regulatory_references.json`. The module indexes 22 curated regulatory profiles, verifying whether "
        "a substance is permitted in India under FSSAI regulations, identifying European Union authorization under EFSA, and displaying "
        "Codex General Standard for Food Additives (CXS 192-1995) provisions. This enables consumers to review verifiable regulatory citations "
        "directly alongside their personalized results."
    )

    # 5.14 Human-in-the-Loop Audit Queue
    builder.add_h1("5.14 Human-in-the-Loop (HITL) Audit Queue and Reviewer Workflow")
    builder.add_p(
        "Encapsulated in `backend/services/audit.py` and rendered via `AuditQueueModal.jsx`, the HITL audit queue intercepts transactions "
        "exhibiting low confidence. An audit record is automatically logged when: (1) unmapped candidate tokens are detected; (2) additive "
        "matching confidence $C_{\\text{additive}} < 0.75$; (3) OCR confidence $C_{\\text{ocr}} < 0.70$; or (4) barcode checksum fails. "
        "Authorized quality reviewers can inspect flagged records, confirm novel additive synonyms, correct typographical misreads, or "
        "reject spurious noise, continuously refining the underlying taxonomy."
    )

    # 5.15 Historical Analysis Storage and Reporting
    builder.add_h1("5.15 Historical Analysis Storage and Reporting Module")
    builder.add_p(
        "Implemented in `backend/services/personal_scoring.py`, completed verification analyses are persisted into the SQLite "
        "`analysis_history` table. Consumers can review past scans via `AnalysisHistoryView.jsx`, apply search filters across product names "
        "and EAN codes, filter by compatibility verdicts, and export historical logs in JSON or CSV format."
    )

    # 5.16 User Interface Engineering & Screenshots
    builder.add_h1("5.16 User Interface Engineering: Minimalist Health-Tech Implementation")
    builder.add_p(
        "The user interface was engineered to embody a modern Minimalist Health-Tech aesthetic, utilizing Neon Lime Green (`#D6FF65`), "
        "Light Grey (`#F4F4F4`), Pure White (`#FFFFFF`), and High-Contrast Dark Text (`#111111`). All technical jargon, redundant banners, "
        "and duplicate buttons were removed from the primary consumer journey, while deep optical metrics were relocated into expandable "
        "accordions. Figures 5.2 through 5.10 illustrate the authentic, running application views."
    )

    # Insert Figures 5.2 to 5.10
    builder.add_figure("Figure 5.2: Health-Tech Wellness Dashboard Overview (Authentic UI)", "fig_5_2_ui_dashboard.png", width_inches=4.0)
    builder.add_figure("Figure 5.3: Dietary Preferences and Additive Avoidance Configuration (Authentic UI)", "fig_5_3_ui_preferences.png", width_inches=4.0)
    builder.add_figure("Figure 5.4: Food Allergy Selection Grid (Authentic UI)", "fig_5_4_ui_allergies.png", width_inches=4.0)
    builder.add_figure("Figure 5.5: Multimodal Product Scanning Interface (Authentic UI)", "fig_5_5_ui_scanning.png", width_inches=4.0)
    builder.add_figure("Figure 5.6: Personalised Analysis Results and Circular Suitability Gauge (Authentic UI)", "fig_5_6_ui_results.png", width_inches=4.0)
    builder.add_figure("Figure 5.7: Detected Ingredients Breakdown and Regulatory Justifications (Authentic UI)", "fig_5_7_ui_ingredient_breakdown.png", width_inches=4.0)
    builder.add_figure("Figure 5.8: Advanced OCR Preprocessing Comparison Modal (Config A vs Config B) (Authentic UI)", "fig_5_8_ui_ocr_modal.png", width_inches=4.0)
    builder.add_figure("Figure 5.9: Scan History Management and Filtering Interface (Authentic UI)", "fig_5_9_ui_history.png", width_inches=4.0)
    builder.add_figure("Figure 5.10: Human-in-the-Loop (HITL) Audit Queue Interface (Authentic UI)", "fig_5_10_ui_audit_modal.png", width_inches=4.0)

    print("Chapter 5 built successfully.")
