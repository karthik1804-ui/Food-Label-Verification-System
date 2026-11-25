"""
chapter_3.py
Chapter 3: SYSTEM REQUIREMENTS AND ANALYSIS
Revised for genuine academic originality, mathematical attribution,
and strict codebase fidelity.
"""

from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def build_chapter_3(builder):
    builder.add_chapter_title("3", "SYSTEM REQUIREMENTS AND ANALYSIS")

    # 3.1 Feasibility Study
    builder.add_h1("3.1 Feasibility Study")
    builder.add_p(
        "Before proceeding with system design and software construction, an exhaustive feasibility analysis was conducted "
        "across technical, operational, economic, and scheduling dimensions to confirm project viability within an MCA capstone framework."
    )
    builder.add_p(
        "1. Technical Feasibility: The proposed architecture builds upon mature, open-source computer vision and web technologies. "
        "The Python backend leverages OpenCV [26] for image filtering, NumPy [27] for multi-dimensional matrix operations, Tesseract [2] "
        "for optical text recognition, and Flask [28] for lightweight RESTful microservices. The frontend utilizes React 18 for a component-driven "
        "single-page application. All dependencies are accessible as open-source libraries with active community support, confirming technical feasibility.\n\n"
        "2. Operational Feasibility: The software is engineered for deployment on standard commodity hardware (consumer laptops and smartphones). "
        "By enforcing client-side camera access and responsive design adhering to WCAG 2.1 accessibility guidelines [33], the application "
        "requires minimal technical expertise from shoppers, establishing high operational feasibility.\n\n"
        "3. Economic Feasibility: The software stack is composed exclusively of open-source libraries, open data protocols (Open Food Facts [21]), "
        "and public regulatory standards (Codex [9], FSSAI [11]). Development and deployment incur zero licensing fees for proprietary OCR APIs "
        "or commercial database subscriptions, demonstrating complete economic feasibility.\n\n"
        "4. Schedule Feasibility: The development lifecycle was executed iteratively across milestone sprints spanning requirement analysis, "
        "OpenCV preprocessing integration, rule engine formulation, automated testing (187 test cases), and dissertation documentation."
    )

    # 3.2 Stakeholder Analysis & User Personas
    builder.add_h1("3.2 Stakeholder Analysis & User Personas")
    builder.add_p(
        "A rigorous requirements analysis requires identifying the primary user personas who interact with the system. Table 3.1 "
        "summarizes three representative user profiles, their primary health concerns, and their specific system requirements."
    )

    # Table 3.1: User Personas
    headers_t31 = ["User Persona", "Clinical / Dietary Profile", "Primary Packaging Verification Pain Point", "System Requirement & Feature Mapping"]
    data_t31 = [
        ["Health-Conscious Shopper", "Clean-Eating / Low Additives", "Difficult to identify synthetic preservatives and azo dyes hidden behind abstract INS codes.", "Taxonomy lookup mapping INS codes to substance names with toxicity flags."],
        ["Immunogenic Allergy Patient", "Celiac Disease / Peanut Allergy", "Microscopic allergen statements, cross-contact warnings, and cryptic gluten derivatives.", "Zero-tolerance allergen gating with instant statutory penalty deductions."],
        ["Ethical / Religious Consumer", "Strict Vegan / Vegetarian", "Concealed animal-derived additives (Carmine INS 120, Gelatin INS 428, L-Cysteine INS 920).", "Lifestyle profile filtering identifying animal origins behind numerical codes."]
    ]
    builder.add_table("Table 3.1: User Persona Profile Matrix and System Expectations", headers_t31, data_t31,
                      col_widths=[Inches(1.5), Inches(1.5), Inches(2.2), Inches(2.0)])

    # 3.3 Functional Requirements Specification
    builder.add_h1("3.3 Functional Requirements Specification (SRS-FR-01 to FR-08)")
    builder.add_p(
        "Functional requirements delineate the explicit operational behaviors and software capabilities implemented in the application. "
        "Table 3.2 enumerates the primary functional specifications (SRS-FR-01 through SRS-FR-08)."
    )

    # Table 3.2: Functional Requirements
    headers_t32 = ["Requirement ID", "Requirement Title", "Detailed Functional Description", "Verification Module"]
    data_t32 = [
        ["SRS-FR-01", "Barcode Detection & Modulo-10 Validation", "Detect EAN-13 barcodes, decode numeric payload via zbar, and validate integrity using GS1 Modulo-10 checksum algorithm [23].", "Barcode Service (`backend/services/barcode_service.py`)"],
        ["SRS-FR-02", "External Registry & Benchmark Fallback", "Query Open Food Facts REST API [21]; automatically fall back to local benchmark catalog if latency exceeds 4.0s or device is offline.", "Barcode Service (`backend/services/barcode_service.py`)"],
        ["SRS-FR-03", "Adaptive OpenCV Image Preprocessing", "Execute 8-stage image enhancement (Configuration B) incorporating bilateral filtering [6], CLAHE [5], and adaptive thresholding [4], [7].", "Optical Preprocessor (`backend/services/ocr/image_preprocessor.py`)"],
        ["SRS-FR-04", "Tesseract OCR & Automatic Fallback", "Execute Tesseract OCR [2]; detect execution anomalies or empty character streams and automatically fall back to baseline Configuration A.", "OCR Pipeline (`backend/services/ocr/ocr_pipeline.py`)"],
        ["SRS-FR-05", "Text Normalization & INS Regex Parsing", "Apply regex patterns `r'(?:INS\\s*|E\\s*)?(\\d{3,4}[a-z]?)'` and normalize optical substitutions within 100–1599 bounds [9].", "OCR Pipeline (`backend/services/ocr/ocr_pipeline.py`)"],
        ["SRS-FR-06", "750-Entry INS Additive Taxonomy Engine", "Cross-reference extracted tokens against local taxonomy comprising 750 verified additives across 7 functional classes [9], [11].", "Taxonomy Engine (`backend/services/taxonomy_service.py`)"],
        ["SRS-FR-07", "Deterministic Preference & Risk Scoring", "Compute suitability score (0–100) using explicit statutory deductions across 4 lifestyle presets and 11 allergen categories.", "Dietary Risk Engine (`backend/services/risk_engine.py`)"],
        ["SRS-FR-08", "Multimodal Confidence & HITL Triage", "Formulate 4D confidence vector; route scans with optical or taxonomy confidence below 0.60 to administrative audit queue.", "Audit Subsystem (`backend/services/audit_service.py`)"]
    ]
    builder.add_table("Table 3.2: Functional Requirements Specification (SRS-FR-01 to FR-08)", headers_t32, data_t32,
                      col_widths=[Inches(1.0), Inches(1.5), Inches(3.2), Inches(1.5)])

    # 3.4 Non-Functional Requirements Specification
    builder.add_h1("3.4 Non-Functional Requirements Specification (SRS-NFR-01 to NFR-08)")
    builder.add_p(
        "Non-functional requirements specify operational qualities, performance thresholds, and architectural constraints. "
        "Table 3.3 defines the non-functional criteria governing system verification."
    )

    # Table 3.3: Non-Functional Requirements
    headers_t33 = ["Requirement ID", "Quality Attribute", "Performance / Architectural Specification Threshold", "Compliance Metric"]
    data_t33 = [
        ["SRS-NFR-01", "Response Latency", "End-to-end OCR processing latency must execute within 1500 ms for images up to 1800x1800 px on standard hardware.", "p95 Latency <= 1450 ms"],
        ["SRS-NFR-02", "OCR Character Error Rate", "Enhanced Configuration B must reduce Character Error Rate (CER) by at least 30% relative to unaugmented Configuration A on curved packaging.", "Verified CER <= 4.2%"],
        ["SRS-NFR-03", "System Availability", "The system must maintain 99.5% operational availability, with automatic offline fallback when external REST APIs become unreachable.", "Zero-Crash Fallback"],
        ["SRS-NFR-04", "Authentication Security", "User passwords must be salted and hashed using PBKDF2-HMAC-SHA256 with >=100,000 iterations adhering to RFC 2898 [30].", "NIST SP 800-132 Compliant"],
        ["SRS-NFR-05", "Data Storage Integrity", "Relational entities must enforce strict referential integrity, foreign key constraints, and parameterized SQL queries in SQLite [31].", "Zero SQL Injection Vulnerability"],
        ["SRS-NFR-06", "UI Accessibility & Contrast", "Frontend color palette must achieve WCAG 2.1 AA compliance [33] with contrast ratios >= 4.5:1 for all text elements.", "Contrast Ratio >= 4.6:1"],
        ["SRS-NFR-07", "Cross-Platform Responsiveness", "Frontend must render adaptively across viewport widths from 320 px (mobile) to 1920 px (desktop) without layout breaking.", "Responsive Flexbox Layout"],
        ["SRS-NFR-08", "Code Quality & Test Coverage", "The automated test suite must achieve 100% pass rate across at least 180 distinct assertions covering all backend services.", "187 / 187 Passing Tests"]
    ]
    builder.add_table("Table 3.3: Non-Functional Requirements Specification (SRS-NFR-01 to NFR-08)", headers_t33, data_t33,
                      col_widths=[Inches(1.0), Inches(1.3), Inches(3.4), Inches(1.5)])

    # 3.5 Hardware and Environmental Requirements
    builder.add_h1("3.5 Hardware and Environmental Requirements")
    builder.add_p(
        "Table 3.4 outlines the hardware specifications for both development/server environments and client mobile devices."
    )

    # Table 3.4: Hardware Requirements
    headers_t34 = ["Component Parameter", "Development / Server Station Minimum", "Client Consumer Device Minimum"]
    data_t34 = [
        ["Processor (CPU)", "Quad-Core x86_64 CPU @ 2.4 GHz (Intel Core i5 / AMD Ryzen 5)", "ARM64 Dual-Core CPU @ 1.8 GHz or modern multi-core mobile SoC"],
        ["System Memory (RAM)", "8.0 GB DDR4 System RAM (16.0 GB Recommended)", "3.0 GB Mobile LPDDR4 RAM"],
        ["Storage Space", "10.0 GB Available SSD Storage (for Python virtualenv, Tesseract traineddata)", "150 MB Storage for browser cache and offline assets"],
        ["Optical Capture Device", "Integrated 1080p Web Camera or Mobile Hotspot Camera", "5.0 Megapixel Rear-Facing Camera with autofocus and LED flash"],
        ["Network Interface", "Standard Wi-Fi (802.11ac) or Gigabit Ethernet (1000 Mbps)", "3G/4G/5G Cellular Data or Wi-Fi (Offline mode supported)"]
    ]
    builder.add_table("Table 3.4: Hardware and Client Device Engineering Specifications", headers_t34, data_t34,
                      col_widths=[Inches(1.8), Inches(2.7), Inches(2.7)])

    # 3.6 Software Technology Stack and Framework Justifications
    builder.add_h1("3.6 Software Technology Stack and Framework Justifications")
    builder.add_p(
        "Table 3.5 summarizes the software libraries, frameworks, and tools selected for the implementation."
    )

    # Table 3.5: Software Stack
    headers_t35 = ["Layer / Subsystem", "Technology / Framework", "Selected Version", "Engineering Justification and Role in System"]
    data_t35 = [
        ["Backend Runtime", "Python", "3.10 / 3.14", "Core programming language offering extensive scientific computing and computer vision libraries."],
        ["API Web Framework", "Flask", "3.0.0+", "Lightweight WSGI web microframework [28] providing rapid routing, CORS support, and low memory footprint."],
        ["Computer Vision Engine", "OpenCV (opencv-python)", "4.8.0 / 4.10.0", "Industry-standard vision library [26] used for image filtering, CLAHE, resizing, and denoising."],
        ["Numerical Computing", "NumPy", "1.24.0+", "High-performance N-dimensional array processing [27] utilized for pixel manipulation and truth-value checks."],
        ["OCR Engine", "Tesseract OCR / pytesseract", "5.4.0", "LSTM neural network character recognition engine [2] executing text transcription."],
        ["Barcode Processing", "pyzbar / zbar", "0.1.9+", "Open-source barcode scanning library reading EAN-13 symbologies from digital imagery."],
        ["Database Engine", "SQLite", "3.42+", "Serverless, ACID-compliant relational database [31] for persistent user profiles, scan cache, and audit queues."],
        ["Frontend UI Framework", "React", "18.2.0 / 19.x", "Component-driven JavaScript library for high-responsiveness single-page application rendering."],
        ["Icons & Visual Styling", "Lucide React & Tailwind CSS", "0.300+ / 3.4+", "Clean, accessible SVG iconography and modular styling supporting the Neon Lime health-tech theme."],
        ["Quality Assurance", "unittest / pytest", "Python Built-in", "Automated test runner executing 187 comprehensive unit, integration, and regression test cases."]
    ]
    builder.add_table("Table 3.5: Software Frameworks, Libraries, and Runtime Dependencies", headers_t35, data_t35,
                      col_widths=[Inches(1.5), Inches(1.5), Inches(1.0), Inches(3.2)])

    # 3.7 Mathematical Modeling & Algorithmic Formulations
    builder.add_h1("3.7 Mathematical Modeling & Algorithmic Formulations")
    builder.add_p(
        "To ensure deterministic execution and scientific reproducibility, core system operations are formalized mathematically:\n\n"
        "1. Contrast-Limited Adaptive Histogram Equalization (CLAHE): Formulated by Zuiderveld [5], CLAHE divides the input image "
        "into $M \\times N$ contextual grid tiles. In each tile, the local gray-level histogram $h(k)$ is computed. To prevent noise amplification, "
        "the histogram is clipped at threshold $\\beta$, and the excess pixels are redistributed uniformly. The transfer function for local equalization is:"
    )
    builder.add_p(
        "$$g(x,y) = \\left[\\frac{L-1}{M \\times N} \\sum_{k=0}^{f(x,y)} h_{\\text{clipped}}(k)\\right]$$"
    )
    builder.add_p(
        "where $L$ denotes the total number of gray levels ($L=256$), $f(x,y)$ represents the input pixel intensity, and bilinear interpolation "
        "is applied across tile boundaries to eliminate blocking artifacts [5].\n\n"
        "2. Gaussian Bilateral Filtering: Formulated by Tomasi and Manduchi [6], the bilateral filter smooths background packaging textures "
        "while strictly preserving character edge boundaries by combining spatial geometric distance with radiometric photometric similarity:"
    )
    builder.add_p(
        "$$I^{\\text{filtered}}(x) = \\frac{1}{W_p} \\sum_{x_i \\in \\Omega} I(x_i) \\cdot \\exp\\left(-\\frac{\\|x_i - x\\|^2}{2\\sigma_s^2}\\right) \\cdot \\exp\\left(-\\frac{\\|I(x_i) - I(x)\\|^2}{2\\sigma_r^2}\\right)$$"
    )
    builder.add_p(
        "where $\\Omega$ represents the spatial neighborhood centered at pixel $x$, $\\sigma_s$ controls spatial smoothing, $\\sigma_r$ controls "
        "radiometric edge selectivity, and $W_p$ denotes the normalization factor [6].\n\n"
        "3. GS1 EAN-13 Check Digit Calculation: Governed by GS1 standards [23], the 13th digit of an EAN-13 barcode $d_{13}$ is verified "
        "via the Modulo-10 weighted sum:"
    )
    builder.add_p(
        "$$S = \\sum_{i=1}^{12} d_i \\cdot w_i, \\quad \\text{where } w_i = \\begin{cases} 1 & \\text{if } i \\text{ is odd} \\\\ 3 & \\text{if } i \\text{ is even} \\end{cases}$$"
    )
    builder.add_p(
        "$$d_{13} = (10 - (S \\bmod 10)) \\bmod 10$$"
    )
    builder.add_p(
        "4. Deterministic Dietary Suitability Score: Implemented in `backend/services/risk_engine.py`, the final suitability score "
        "$S_{\\text{final}} \\in [0, 100]$ applies deterministic statutory penalty deductions:"
    )
    builder.add_p(
        "$$S_{\\text{final}} = \\max\\left(0, 100 - \\left[\\sum_{j \\in \\mathcal{A}} w_{\\text{allergen}} \\cdot I_j + \\sum_{k \\in \\mathcal{L}} w_{\\text{lifestyle}} \\cdot I_k + \\sum_{m \\in \\mathcal{D}} w_{\\text{flag}} \\cdot I_m\\right]\\right)$$"
    )
    builder.add_p(
        "where $w_{\\text{allergen}} = 50$ (or an immediate zero override if marked severe), $w_{\\text{lifestyle}} = 30$, and $w_{\\text{flag}} = 15$.\n\n"
        "5. Multimodal Confidence Vector Formulation: The overall verification certainty $C_{\\text{multimodal}} \\in [0, 1]$ is computed as:"
    )
    builder.add_p(
        "$$C_{\\text{multimodal}} = 0.40 \\cdot C_{\\text{OCR}} + 0.35 \\cdot C_{\\text{taxonomy}} + 0.25 \\cdot C_{\\text{prep}}$$"
    )

    # Insert Figure 3.1
    builder.add_figure(
        "Figure 3.1: Functional Decomposition Hierarchy of Proposed System",
        "fig_3_1_functional_decomposition.png",
        width_inches=4.8
    )

    # 3.8 Error Handling, Edge Cases, and Boundary Conditions
    builder.add_h1("3.8 Error Handling, Edge Cases, and Boundary Conditions")
    builder.add_p(
        "Table 3.6 details the boundary conditions and graceful degradation strategies engineered into the system."
    )

    # Table 3.6: Boundary Conditions
    headers_t36 = ["Boundary Condition / Edge Case", "Root Cause & Physical Manifestation", "System Countermeasure & Recovery Protocol", "Test Assertion Reference"]
    data_t36 = [
        ["Severely Blurred Packaging", "Motion blur or optical defocusing ($L_{\\text{var}} < 100$).", "Configuration B flags blur; applies unsharp mask; logs low preprocessing confidence.", "Test `test_blur_detection`"],
        ["Damaged / Scratched Barcode", "Incomplete vertical guard bars or printing tear.", "Modulo-10 checksum fails; system rejects code and prompts user to scan text label directly.", "Test `test_invalid_checksum`"],
        ["External REST API Timeout", "Network latency or Open Food Facts downtime (>4.0s).", "System aborts HTTP request and seamlessly returns matching record from local benchmark catalog.", "Test `test_offline_fallback`"],
        ["Extreme Specular Glare", "Cellophane wrapper reflecting direct retail spotlight.", "CLAHE redistributes local luminance; fallback to Configuration A if B yields empty mask.", "Test `test_glare_handling`"],
        ["Unmapped Chemical Term", "Rare additive or novel commercial synonym not in INS catalog.", "Extracts raw text; flags unmapped status; automatically enqueues candidate into HITL audit queue.", "Test `test_audit_enqueuing`"]
    ]
    builder.add_table("Table 3.6: Boundary Conditions, Failure Modes, and Resilient Fallback Strategies", headers_t36, data_t36,
                      col_widths=[Inches(1.5), Inches(1.8), Inches(2.7), Inches(1.2)])

    # 3.9 Human-in-the-Loop Workflow Mechanics
    builder.add_h1("3.9 Human-in-the-Loop (HITL) Workflow Mechanics")
    builder.add_p(
        "To ensure continuous dictionary expansion without compromising safety, the system incorporates an administrative HITL triage queue "
        "implemented in `backend/services/audit_service.py`. When an extracted chemical term fails to map to the 750-entry taxonomy or the "
        "multimodal confidence falls below 0.60, the scan record is flagged as `NEEDS_AUDIT`. Authorized reviewers inspect the physical "
        "crop, verify the chemical identity against Codex schedules [9], and approve or reject the token into the active taxonomy."
    )

    # 3.10 Summary of Analytical Foundations
    builder.add_h1("3.10 Summary of Analytical Foundations")
    builder.add_p(
        "The requirements analysis establishes a mathematically grounded, fault-tolerant foundation for the system architecture. "
        "By enforcing decoupled execution, deterministic rule deductions, and confidence-gated human audit, the system eliminates "
        "the fragility and hallucinations characteristic of prior monolithic approaches."
    )

    print("Chapter 3 built successfully.")
