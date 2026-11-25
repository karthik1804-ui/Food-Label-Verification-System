"""
chapter_5.py
Chapter 5: SYSTEM IMPLEMENTATION
Revised for genuine academic originality, IEEE in-text citation linking,
and strict codebase fidelity.
"""

from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def build_chapter_5(builder):
    builder.add_chapter_title("5", "SYSTEM IMPLEMENTATION")

    # 5.1 Development Environment Setup and Configuration
    builder.add_h1("5.1 Development Environment Setup and Configuration")
    builder.add_p(
        "The implementation was engineered using a modular full-stack architecture comprising a Python Flask backend [28] "
        "and a React 18 Single-Page Application (SPA). Development was conducted within isolated virtual environments "
        "enforcing strict dependency locking. The computer vision layer incorporates OpenCV 4.10 [26] and NumPy [27], "
        "interfacing with Tesseract OCR 5.4.0 [2] via pytesseract. The relational database is managed through SQLite [31], "
        "while client-side state is orchestrated via React Hooks and Lucide React iconography adhering to the Neon Lime health-tech theme."
    )

    # 5.2 Full-Stack Implementation Overview
    builder.add_h1("5.2 Full-Stack Implementation Overview")
    builder.add_p(
        "The backend software architecture is partitioned into seven distinct service modules located in `backend/services/`:\n\n"
        "• `barcode_service.py`: Encapsulates zbar optical detection, GS1 Modulo-10 checksum validation [23], Open Food Facts REST integration [21], and local benchmark catalog fallback.\n\n"
        "• `image_preprocessor.py`: Implements the 8-stage OpenCV image enhancement workflow (Configuration B) [26], including bilateral filtering [6], CLAHE [5], and adaptive thresholding [4], [7].\n\n"
        "• `ocr_pipeline.py`: Orchestrates dual-configuration optical execution, managing automatic fallback from Configuration B to Configuration A and enforcing page segmentation modes [2].\n\n"
        "• `taxonomy_service.py`: Ingests and indexes the 750-entry Codex Alimentarius INS taxonomy [9] from `backend/data/ins_taxonomy.json`.\n\n"
        "• `risk_engine.py`: Executes deterministic, rule-based dietary risk scoring across 4 lifestyle presets and 11 allergen categories.\n\n"
        "• `audit_service.py`: Formulates the 4-dimensional multimodal confidence vector and manages administrative triage for unmapped chemical candidates.\n\n"
        "• `app.py`: Implements the Flask application gateway [28], route controllers, error serialization, and PBKDF2 authentication [30]."
    )

    # 5.3 Authentication, Token Management, and PBKDF2 Password Hashing
    builder.add_h1("5.3 Authentication, Token Management, and PBKDF2 Password Hashing")
    builder.add_p(
        "User authentication is implemented in `backend/app.py` adhering to NIST Special Publication 800-132 recommendations. "
        "Passwords are never stored in plaintext; instead, they are hashed using the Password-Based Key Derivation Function 2 (PBKDF2) "
        "with HMAC-SHA256 and a random 16-byte salt across 100,000 iterations, adhering to IETF RFC 2898 [30]. Session tokens are "
        "cryptographically signed, enabling stateless authentication across RESTful endpoints while protecting user dietary profiles."
    )

    # 5.4 Barcode Detection, Checksum Verification, and Database Lookup
    builder.add_h1("5.4 Barcode Detection, Checksum Verification, and Database Lookup")
    builder.add_p(
        "Pipeline A execution is governed by `backend/services/barcode_service.py`. When an image containing an EAN-13 barcode is uploaded, "
        "pyzbar extracts the optical digit sequence. The service immediately verifies mathematical integrity via the Modulo-10 checksum algorithm [23]. "
        "If the check digit matches, the service queries the Open Food Facts API (`https://world.openfoodfacts.org/api/v0/product/{barcode}.json`) [21]. "
        "To ensure high availability during network latency or offline scenarios, the service implements a 4.0-second timeout that automatically "
        "falls back to a curated local benchmark catalog (`data/offline_benchmark_products.json`), guaranteeing uninterrupted user verification."
    )

    # 5.5 OpenCV Image Preprocessing Implementation (Configuration B)
    builder.add_h1("5.5 OpenCV Image Preprocessing Implementation (Configuration B)")
    builder.add_p(
        "The core computer vision logic is encapsulated in `backend/services/ocr/image_preprocessor.py`. In enhanced Configuration B, "
        "the preprocessor executes an 8-stage transformation pipeline designed to stabilize contrast on curved, non-planar packaging surfaces:\n\n"
        "1. Image Preparation Validation: Rejects invalid, empty, or corrupted byte streams; validates channel layout (supporting BGR and Grayscale); "
        "and performs aspect-ratio preserving downscaling if the maximum dimension exceeds 1800 px.\n\n"
        "2. Dual-Channel Image Preparation: To optimize text boundary contrast, the preprocessor constructs two distinct prepared representations: "
        "a Grayscale array and an edge-filtered luminance array. Strict NumPy array truth-value checks (`if arr is not None:`) are enforced "
        "to prevent ambiguous boolean evaluation errors.\n\n"
        "3. Blur Quantification: Computes the variance of the Laplacian operator: $L_{\\text{var}} = \\text{Var}(\\nabla^2 I)$. If $L_{\\text{var}} < 100$, "
        "the image is flagged as optically blurred, and a controlled $3 \\times 3$ unsharp mask kernel is applied.\n\n"
        "4. Gaussian Bilateral Smoothing: Applies `cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)` [6] to suppress cellophane "
        "noise while preserving sharp character stroke edges.\n\n"
        "5. Contrast-Limited Adaptive Equalization: Applies `cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8,8))` [5] to equalize local luminance "
        "gradients caused by directional store lighting.\n\n"
        "6. Adaptive Morphological Operations: Deploys a $3 \\times 3$ rectangular structuring element to close minute gaps in broken character kerning.\n\n"
        "7. Dynamic Adaptive Thresholding: Computes locally binarized text masks using `cv2.adaptiveThreshold` with Gaussian windowing [4], [7].\n\n"
        "8. Region Extraction: Isolates candidate text regions for Tesseract line recognition."
    )

    # Table 5.1: Configuration Parameters
    headers_t51 = ["Preprocessing Parameter", "Baseline Configuration A", "Enhanced Configuration B", "Engineering Justification"]
    data_t51 = [
        ["Max Dimension Boundary", "Unconstrained (Original)", "1800 px (Aspect Preserved)", "Prevents memory saturation during high-res mobile uploads."],
        ["Color Space Conversion", "Standard BGR / RGB", "Grayscale + ITU-R BT.601", "Standardizes single-channel luminance for OCR processing."],
        ["Blur Detection & Sharpening", "None (Disabled)", "Laplacian Var (Threshold=100)", "Quantifies optical defocusing and applies unsharp masking."],
        ["Noise Suppression Filter", "None (Raw Pixels)", "Bilateral Filter (d=9, s=75)", "Smooths packaging texture without blurring character stroke edges."],
        ["Luminance Normalization", "None (Global Raw)", "CLAHE (Clip=2.5, Tile=8x8)", "Normalizes severe lighting gradients and specular cellophane glare."],
        ["Binarization Method", "Otsu Global Threshold", "Adaptive Gaussian Threshold", "Computes dynamic local thresholds resilient to curvature falloff."],
        ["Morphological Structuring", "None (Raw)", "Rectangular Closing (3x3)", "Reconnects broken character kerning in dense 4.5pt typography."]
    ]
    builder.add_table("Table 5.1: OpenCV Configuration B vs. Configuration A Pipeline Parameter Matrix", headers_t51, data_t51,
                      col_widths=[Inches(1.8), Inches(1.5), Inches(1.8), Inches(2.1)])

    # 5.6 Tesseract OCR Execution, Page Segmentation Modes, and Fallback
    builder.add_h1("5.6 Tesseract OCR Execution, Page Segmentation Modes, and Fallback")
    builder.add_p(
        "Optical character recognition is managed by `backend/services/ocr/ocr_pipeline.py`. The service initializes Tesseract 5.4.0 [2] "
        "configured with Page Segmentation Mode (PSM) 6 (assuming a single uniform block of text) and PSM 11 (sparse text with irregular "
        "spacing). The dual-configuration pipeline implements automatic error fallback: if Configuration B encounters an image preparation "
        "anomaly or returns an empty character sequence, the engine immediately catches the exception and executes baseline Configuration A. "
        "This ensures maximum verification availability without crashing."
    )

    # 5.7 OCR Text Normalization, INS Regex Extraction, and Numeric Bounds
    builder.add_h1("5.7 OCR Text Normalization, INS Regex Extraction, and Numeric Bounds")
    builder.add_p(
        "Raw OCR strings are processed through targeted normalization routines. The normalizer applies regular expressions "
        "(`r'(?:INS\\s*|E\\s*|additive\\s*)?(\\d{3,4}[a-z]?)'`) to detect potential additive identifiers. To correct visual misreads "
        "strictly within numeric boundaries, optical character substitution rules are applied (e.g., substituting 'I' or 'l' with '1', 'O' with '0'). "
        "Extracted numbers are validated against the statutory range 100–1599 defined by Codex Alimentarius [9], eliminating false matches "
        "derived from net weights, batch numbers, or telephone digits."
    )

    # 5.8 750-Entry Food Additive Taxonomy Engine Implementation
    builder.add_h1("5.8 750-Entry Food Additive Taxonomy Engine Implementation")
    builder.add_p(
        "The taxonomy engine (`backend/services/taxonomy_service.py`) loads an authoritative catalog of 750 verified food additives "
        "from `backend/data/ins_taxonomy.json`. Each entry contains the standardized INS code, formal chemical title, common trade synonyms, "
        "functional technological category (e.g., Preservative, Color, Emulsifier), official regulatory approval status across Codex [9], "
        "FSSAI [11], and EFSA [13], and health risk flags (e.g., hyperactivity warnings, allergen triggers, animal origins)."
    )

    # 5.9 Deterministic Rule-Based Dietary Risk Engine Implementation
    builder.add_h1("5.9 Deterministic Rule-Based Dietary Risk Engine Implementation")
    builder.add_p(
        "The dietary risk engine (`backend/services/risk_engine.py`) evaluates normalized tokens against user profiles without "
        "probabilistic machine learning guesswork. The system computes a deterministic suitability score from 0 to 100 using explicit "
        "statutory point deductions:\n\n"
        "• Severe Allergen Violation: Deducts 50 points or immediately forces the suitability score to 0 with a high-priority medical alert.\n\n"
        "• Lifestyle Profile Conflict: Deducts 30 points (e.g., animal-derived Gelatin INS 428 in a strict vegan profile).\n\n"
        "• High-Concern Additive Flag: Deducts 15 points (e.g., artificial azo colorants linked to childhood hyperactivity [15]).\n\n"
        "• Mild Technological Additive: Deducts 5 points for general ultra-processed additive accumulation [38]."
    )

    # 5.10 Multimodal Confidence Vector and Audit Triage Implementation
    builder.add_h1("5.10 Multimodal Confidence Vector and Audit Triage Implementation")
    builder.add_p(
        "The audit service (`backend/services/audit_service.py`) calculates the 4-dimensional confidence vector ($C_{\\text{OCR}}$, "
        "$C_{\\text{taxonomy}}$, $C_{\\text{prep}}$, $C_{\\text{barcode}}$). Scans with composite confidence below 0.60 or containing "
        "unmapped chemical candidate strings are stored in SQLite [31] with triage status `NEEDS_AUDIT` for administrative review."
    )

    # 5.11 Human-in-the-Loop Audit Queue and Review Modal Implementation
    builder.add_h1("5.11 Human-in-the-Loop Audit Queue and Review Modal Implementation")
    builder.add_p(
        "The administrative frontend provides an interactive audit review modal (`frontend/src/components/AuditQueueModal.jsx`). "
        "Authorized reviewers inspect high-resolution image crops of flagged text regions, cross-reference candidate strings against "
        "Codex schedules [9], and approve new synonyms into the active taxonomy dictionary or reject false character noise."
    )

    # 5.12 RESTful API Design, Route Controllers, and Error Serialization
    builder.add_h1("5.12 RESTful API Design, Route Controllers, and Error Serialization")
    builder.add_p(
        "The Flask backend [28] exposes clean RESTful endpoints adhering to JSON API standards [29]. Error conditions (such as invalid "
        "image encodings, corrupted barcodes, or unparseable payloads) return standardized HTTP error responses (400 Bad Request, "
        "404 Not Found, 500 Internal Error) with structured diagnostic messages, preventing unhandled runtime exceptions."
    )

    # 5.13 Frontend Architecture: Minimalist Health-Tech UI Design System
    builder.add_h1("5.13 Frontend Architecture: Minimalist Health-Tech UI Design System")
    builder.add_p(
        "The frontend is constructed in React 18, implementing a modern Minimalist Health-Tech design system. The visual theme "
        "combines an energetic Neon Lime Green primary accent (`#D6FF65`), crisp white cards (`#FFFFFF`), a clean clinical light-grey "
        "background (`#F4F4F4`), high-contrast dark text (`#111111`), and Dark Teal structural surfaces (`#00454A`). The interface "
        "delivers high accessibility (WCAG 2.1 AA compliant [33]), rapid visual parsing, and responsive layout across mobile and desktop devices."
    )

    # 5.14 User Interface Screens and Verification Walkthroughs
    builder.add_h1("5.14 User Interface Screens and Verification Walkthroughs (10 Screens)")
    builder.add_p(
        "Figures 5.1 through 5.10 present the ten authentic user interface screens comprising the application."
    )

    # Insert Figures 5.1 to 5.10
    ui_figures = [
        ("Figure 5.1: User Authentication and Registration Interface (Authentic UI)", "fig_5_1_ui_auth.png"),
        ("Figure 5.2: Health-Tech Wellness Dashboard Overview (Authentic UI)", "fig_5_2_ui_dashboard.png"),
        ("Figure 5.3: Dietary Preferences and Additive Avoidance Configuration (Authentic UI)", "fig_5_3_ui_preferences.png"),
        ("Figure 5.4: Food Allergy Selection Grid (Authentic UI)", "fig_5_4_ui_allergies.png"),
        ("Figure 5.5: Multimodal Product Scanning Interface (Authentic UI)", "fig_5_5_ui_scanning.png"),
        ("Figure 5.6: Personalised Analysis Results and Circular Suitability Gauge (Authentic UI)", "fig_5_6_ui_results.png"),
        ("Figure 5.7: Detected Ingredients Breakdown and Regulatory Justifications (Authentic UI)", "fig_5_7_ui_ingredient_breakdown.png"),
        ("Figure 5.8: Advanced OCR Preprocessing Comparison Modal (Config A vs Config B) (Authentic UI)", "fig_5_8_ui_ocr_modal.png"),
        ("Figure 5.9: Scan History Management and Filtering Interface (Authentic UI)", "fig_5_9_ui_history.png"),
        ("Figure 5.10: Human-in-the-Loop (HITL) Audit Queue Interface (Authentic UI)", "fig_5_10_ui_audit_modal.png")
    ]
    for cap, img in ui_figures:
        builder.add_figure(cap, img, width_inches=4.8)

    print("Chapter 5 built successfully.")
