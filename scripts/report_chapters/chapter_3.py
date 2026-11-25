"""
chapter_3.py
Chapter 3: SYSTEM REQUIREMENTS AND ANALYSIS
Details existing system deficiencies, proposed system capabilities,
functional/non-functional requirements, feasibility study, hardware/software specs,
and comprehensive use case specifications.
"""

from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def build_chapter_3(builder):
    builder.add_chapter_title("3", "SYSTEM REQUIREMENTS AND ANALYSIS")

    # 3.1 Analysis of Existing Manual & Commercial Solutions
    builder.add_h1("3.1 Analysis of Existing Manual & Commercial Solutions")
    builder.add_p(
        "To establish rigorous system requirements, a systematic analysis of current consumer methodologies and commercial software "
        "solutions was conducted. In the absence of specialized computational assistance, consumers typically rely on manual visual "
        "inspection of packaging labels. Under real-world retail purchasing conditions, manual inspection suffers from severe cognitive "
        "and physical impediments. Modern supermarket environments present shoppers with thousands of competing packaged commodities, "
        "imposing acute time constraints (typically under 20–30 seconds per product evaluation). Furthermore, packaged food manufacturers "
        "routinely utilize graphic design techniques that comply minimally with statutory print regulations while maximizing informational "
        "obfuscation: ingredient lists are frequently printed in pale gray inks against pastel backgrounds, placed beneath folds or seams "
        "of flexible pouches, or wrapped around the curved necks of bottles."
    )
    builder.add_p(
        "Commercial software alternatives have gained widespread consumer adoption, most prominently mobile barcode scanners such as "
        "Yuka, FoodSwitch, and Open Food Facts Mobile. While these platforms have elevated public consciousness regarding ultra-processed "
        "foods, their reliance on a single optical modality—the EAN-13 barcode—introduces critical operational deficiencies. When a consumer "
        "scans a barcode, the application performs a key-value lookup against an external cloud database. The consumer is presented with a "
        "pre-calculated score (such as the Nutri-Score algorithm developed by the French public health agency Santé Publique France). "
        "However, as detailed in Table 3.1, this operational model fails to verify whether the physical product package matches the cloud record."
    )

    # Table 3.1: Deficiencies of Existing Systems
    headers_t31 = ["Deficiency Category", "Operational Mechanism in Existing Systems", "Clinical / Consumer Consequence"]
    data_t31 = [
        ["Decoupling from Physical Item", "Queries centralized crowd-sourced database via EAN-13 barcode without verifying physical text.", "Exposes consumers to reformulated ingredients and undeclared allergens when brands alter formulas."],
        ["Lack of Optical Preprocessing", "Direct feed of raw camera snapshots into standard OCR engines without curvature/blur compensation.", "Catastrophic optical character error rates (>25%) on glossy foils, curved bottles, and tiny kerning."],
        ["Truncated Additive Dictionaries", "Keyword search restricted to small static dictionaries (<50 common additive names).", "Fails to identify hundreds of valid INS codes, chemical synonyms, and sub-classified additive derivatives."],
        ["Opaque Scoring Models", "Aggregates overall nutritional quality into a single score; obscures specific additive penalties.", "Fails to alert celiac or allergic consumers when an otherwise 'healthy' item contains lethal allergen traces."],
        ["Zero Quality Gating", "Emits definitive ratings regardless of image blur or unmapped chemical terms.", "Silent guessing on corrupt character noise; misleads users without confidence transparency."]
    ]
    builder.add_table("Table 3.1: Deficiencies of Existing Food Verification Systems", headers_t31, data_t31,
                      col_widths=[Inches(1.8), Inches(2.7), Inches(2.7)])

    # 3.2 Limitations of Monolithic Verification Approaches
    builder.add_h1("3.2 Limitations of Monolithic Verification Approaches")
    builder.add_p(
        "In response to the limitations of barcode-only scanning, early academic systems proposed monolithic verification architectures. "
        "Under a monolithic architecture, a single computational pipeline attempts to ingest a camera snapshot, segment both the barcode "
        "and textual areas, extract OCR text, retrieve online database records, and execute automated cross-source ingredient comparison. "
        "Extensive empirical analysis reveals that monolithic architectures suffer from structural fragility across three dimensions:\n\n"
        "1. Spurious Mismatch Cascades: When a monolithic pipeline attempts to match OCR-extracted ingredient text against crowd-sourced "
        "database text, the comparison frequently triggers false-negative alarms. Packaging text employs non-standard formatting, differing "
        "punctuation, abbreviated chemical descriptors, and localized language variants. Because the string matching threshold must be "
        "artificially strict to detect critical allergens, cosmetic formatting variances cause the monolithic comparator to falsely declare "
        "that the physical package is fraudulent or corrupted.\n\n"
        "2. Cascading Pipeline Failure: In a monolithic system, failure in any single component—such as an obscured barcode, an unlisted "
        "regional product, or a network timeout—halts the entire verification process, denying the user access to optical ingredient analysis "
        "even when the physical packaging text is perfectly legible.\n\n"
        "3. Computational Inefficiency: Forcing simultaneous heavy deep-learning segmentation models on mobile hardware drains battery life "
        "and introduces unacceptable latencies (>4.5 seconds per scan), destroying interactive point-of-sale utility."
    )

    # 3.3 Proposed Decoupled Multimodal System Architecture
    builder.add_h1("3.3 Proposed Decoupled Multimodal System Architecture")
    builder.add_p(
        "To decisively overcome the structural flaws of monolithic systems, this project formulates a Decoupled Multimodal Architecture. "
        "Under this paradigm, the system bifurcates verification into two independent, specialized analytical pipelines that operate "
        "asynchronously and converge exclusively at the unified presentation layer:\n\n"
        "• Pipeline A (Product Identification Pipeline): Focuses strictly on product identity resolution. It decodes the EAN-13 barcode, "
        "validates mathematical integrity via the Modulo-10 checksum algorithm, and queries the Open Food Facts international registry. "
        "If the barcode is missing or the product is unlisted, Pipeline A reports a discrete status without obstructing ingredient analysis.\n\n"
        "• Pipeline B (Personalised Dietary Analysis Pipeline): Operates directly and autonomously on packaging label imagery. It processes "
        "images through an 8-stage OpenCV preprocessing engine (Configuration B), extracts text via Tesseract OCR, normalizes optical typos, "
        "enforces Codex Alimentarius range filters (100–1599), maps tokens against an authoritative 750-entry INS taxonomy, and executes "
        "deterministic dietary scoring against user-configured profiles."
    )

    # Insert Figure 3.1
    builder.add_figure(
        "Figure 3.1: Functional Decomposition Hierarchy of Proposed System",
        "fig_3_1_functional_decomposition.png",
        width_inches=4.0
    )

    # 3.4 Comparative Advantages of the Proposed Solution
    builder.add_h1("3.4 Comparative Advantages of the Proposed Solution")
    builder.add_p(
        "The proposed decoupled multimodal architecture yields distinct technical and operational advantages over existing systems:\n\n"
        "1. Resilient Operational Continuity: The system functions seamlessly whether the user provides a barcode, a packaging image, "
        "both, or raw pasted text. Failure or absence of the barcode does not impede complete optical ingredient verification.\n\n"
        "2. Elimination of Spurious Mismatches: By deliberately avoiding direct cross-source string comparison between OCR text and "
        "crowd-sourced database text, the system completely eliminates reflection- and punctuation-induced false alarms.\n\n"
        "3. High-Fidelity Optical Preprocessing: The 8-stage OpenCV pipeline (CLAHE, bilateral denoising, unsharp masking, adaptive "
        "thresholding) dramatically elevates Tesseract character recognition accuracy on curved, reflective packaging.\n\n"
        "4. Deterministic Explainability: Suitability scores (0–100) are computed via transparent mathematical deductions grounded in "
        "authoritative international statutes (Codex, FSSAI, EFSA). No black-box machine-learning hallucinations compromise health safety.\n\n"
        "5. Confidence-Aware Gating and Audit Protocol: The 4-dimensional confidence vector actively monitors recognition quality and "
        "routes ambiguous or unmapped chemical strings to the Human-in-the-Loop audit queue."
    )

    # 3.5 Functional Requirements Specification (FRS)
    builder.add_h1("3.5 Functional Requirements Specification (FRS)")
    builder.add_p(
        "The functional requirements delineate the concrete software capabilities that the Food Label Verification System must execute. "
        "Table 3.2 compiles the complete functional specifications categorized by operational subsystem."
    )

    # Table 3.2: FRS
    headers_t32 = ["Requirement ID", "Functional Module", "Functional Requirement Description", "Priority"]
    data_t32 = [
        ["FR-01", "Authentication", "System shall authenticate users using PBKDF2-SHA256 hashed credentials and issue secure session tokens.", "Mandatory"],
        ["FR-02", "Dietary Profile", "System shall maintain personalized user dietary profiles supporting 4 lifestyle presets and custom toggles.", "Mandatory"],
        ["FR-03", "Allergen Grid", "System shall allow configuration of 11 regulated allergen categories and enforce CRITICAL deduction rules.", "Mandatory"],
        ["FR-04", "Barcode Decoding", "System shall detect, crop, and decode EAN-13 barcodes from camera streams or uploaded images.", "Mandatory"],
        ["FR-05", "Checksum Validation", "System shall validate all 13-digit barcodes using the standard Modulo-10 checksum algorithm.", "Mandatory"],
        ["FR-06", "Catalog Integration", "System shall query Open Food Facts REST API with 4.0s timeout and fall back to local benchmark catalog.", "Mandatory"],
        ["FR-07", "Image Validation", "System shall reject corrupted buffers and enforce memory boundaries (<=25MB, <=25MP, <=4096px).", "Mandatory"],
        ["FR-08", "OpenCV Preprocessing", "System shall execute 8-stage image enhancement (aspect resizing, bilateral, CLAHE, unsharp mask).", "Mandatory"],
        ["FR-09", "Dual OCR Pipeline", "System shall support Configuration A (Baseline) and Configuration B (OpenCV) with automatic fallback.", "Mandatory"],
        ["FR-10", "Typo Normalization", "System shall correct visual character confusions (I->1, O->0, 1NS->INS) strictly in INS contexts.", "Mandatory"],
        ["FR-11", "Codex Range Check", "System shall validate that extracted E-numbers fall strictly within the 100-1599 additive range.", "Mandatory"],
        ["FR-12", "Taxonomy Mapping", "System shall cross-reference detected tokens against the 750-entry INS taxonomy across 7 classes.", "Mandatory"],
        ["FR-13", "Suitability Scoring", "System shall compute deterministic personal suitability scores (0-100) with explicit rule penalties.", "Mandatory"],
        ["FR-14", "Confidence Modeling", "System shall formulate a 4D confidence vector [C_ocr, C_add, S_bar, C_id] for every scan.", "Mandatory"],
        ["FR-15", "HITL Audit Queue", "System shall log unmapped tokens to audit queue and support auditor confirm, correct, and reject actions.", "Mandatory"],
        ["FR-16", "History & Export", "System shall persist scan history to SQLite with search filters and JSON/CSV export capabilities.", "Mandatory"]
    ]
    builder.add_table("Table 3.2: Functional Requirements Specification (FRS) Summary", headers_t32, data_t32,
                      col_widths=[Inches(1.0), Inches(1.3), Inches(4.0), Inches(0.9)])

    # 3.6 Non-Functional Requirements Specification (NFRS)
    builder.add_h1("3.6 Non-Functional Requirements Specification (NFRS)")
    builder.add_p(
        "Non-functional requirements specify the operational quality criteria, performance constraints, and architectural standards "
        "governing system execution. Table 3.3 presents the NFRS matrix across performance, reliability, security, and usability."
    )

    # Table 3.3: NFRS
    headers_t33 = ["Quality Attribute", "Metric / Constraint", "Target Specification Threshold", "Verification Method"]
    data_t33 = [
        ["Execution Latency", "End-to-end scan response time", "< 1500 ms on standard 1080p label image", "Empirical benchmarking (timings_ms)"],
        ["Preprocessing Time", "OpenCV 8-stage pipeline latency", "< 250 ms on CPU without GPU acceleration", "System timer logging (`cv2.getTickCount`)"],
        ["OCR Accuracy (CER)", "Character Error Rate on INS codes", "< 5.0% on curved/reflective food packaging", "Comparative benchmark against baseline"],
        ["Availability", "System uptime and service continuity", "99.5% uptime; 100% offline fallback resilience", "Mocked network isolation unit tests"],
        ["Memory Safety", "Maximum RAM footprint per request", "< 128 MB RAM per concurrent worker process", "Memory profiling with 25MP decompression bounds"],
        ["Data Security", "Password storage and token protection", "PBKDF2-SHA256 (>=100,000 iterations); bearer tokens", "Cryptographic schema inspection"],
        ["Database Integrity", "Relational consistency and constraints", "PRAGMA foreign_keys = ON; cascade deletes", "Automated foreign-key integrity test suite"],
        ["UI Accessibility", "Contrast and readability compliance", "WCAG 2.1 AA compliant (dark text on lime green)", "Lighthouse accessibility audit"]
    ]
    builder.add_table("Table 3.3: Non-Functional Requirements Specification (NFRS) Matrix", headers_t33, data_t33,
                      col_widths=[Inches(1.3), Inches(1.8), Inches(2.7), Inches(1.4)])

    # 3.7 Operational, Technical, and Economic Feasibility Study
    builder.add_h1("3.7 Operational, Technical, and Economic Feasibility Study")
    builder.add_p(
        "A formal feasibility study was conducted across three essential organizational dimensions:\n\n"
        "1. Technical Feasibility: The project utilizes proven, mature, open-source computational technologies. The Python 3.14 backend "
        "integrates Flask 3.1.3, OpenCV 4.13, and Tesseract 5.0. All components operate efficiently on standard x86-64 and ARM architectures "
        "without requiring specialized GPU clusters. The React 18 SPA frontend executes within any modern web browser supporting HTML5 "
        "Canvas and WebRTC camera APIs. Technical feasibility is fully verified.\n\n"
        "2. Economic Feasibility: The entire software architecture is engineered using open-source frameworks governed by permissive "
        "licenses (MIT, Apache 2.0, BSD). The system leverages the free public Open Food Facts API and utilizes a serverless, zero-maintenance "
        "SQLite 3 database. Capital expenditures for commercial licenses, proprietary OCR cloud APIs, or enterprise database servers are "
        "strictly zero, ensuring complete economic feasibility.\n\n"
        "3. Operational Feasibility: The user interface is engineered under the Minimalist Health-Tech design language. By eliminating "
        "confusing biochemical jargon, duplicate buttons, and cluttered widgets, the system can be operated intuitively by consumers of "
        "all age groups with zero formal training. Operational feasibility is outstanding."
    )

    # 3.8 Hardware Requirements
    builder.add_h1("3.8 Hardware and Computational Environment Requirements")
    builder.add_p(
        "The system is architected to operate across lightweight consumer edge devices and standard commodity server infrastructure. "
        "Table 3.4 outlines the minimum and recommended hardware specifications."
    )

    # Table 3.4: Hardware Specs
    headers_t34 = ["Hardware Component", "Minimum Development Specification", "Recommended Production Specification"]
    data_t34 = [
        ["Processor (CPU)", "Dual-Core x86-64 / ARM64 @ 2.0 GHz", "Quad-Core Intel Core i5 / AMD Ryzen 5 @ 3.2 GHz or higher"],
        ["System Memory (RAM)", "4 GB DDR4 RAM", "8 GB to 16 GB DDR4/DDR5 RAM"],
        ["Storage Space", "2 GB available SSD / HDD space", "10 GB NVMe SSD space (for logs and SQLite database)"],
        ["Camera / Optical Sensor", "720p HD resolution camera (1280x720)", "1080p Full HD resolution camera with auto-focus"],
        ["Network Interface", "Standard Wi-Fi or 4G LTE connection", "Broadband Internet connection (for Open Food Facts REST lookup)"]
    ]
    builder.add_table("Table 3.4: Hardware Development and Deployment Specifications", headers_t34, data_t34,
                      col_widths=[Inches(1.8), Inches(2.7), Inches(2.7)])

    # 3.9 Software Specifications
    builder.add_h1("3.9 Software Specifications, Libraries, and Technology Stack")
    builder.add_p(
        "The software architecture enforces strict version stability and dependency decoupling. Table 3.5 compiles the verified software "
        "specifications and library dependencies."
    )

    # Table 3.5: Software Dependencies
    headers_t35 = ["Software Layer", "Framework / Library Name", "Version", "Operational Purpose in Architecture"]
    data_t35 = [
        ["Runtime Environment", "Python", "3.14.0", "Core backend execution runtime and service hosting"],
        ["Web Framework", "Flask", "3.1.3", "REST API routing, request validation, and JSON serialization"],
        ["Computer Vision", "OpenCV (opencv-python)", "4.13.0.92", "Image validation, CLAHE, bilateral filtering, blur grading"],
        ["OCR Engine", "Tesseract OCR / pytesseract", "5.0.0 / 0.3.10", "Optical character recognition and word confidence extraction"],
        ["Numerical Computing", "NumPy", "2.4.5", "Array manipulation, matrix mathematics, Laplacian variance"],
        ["Database Engine", "SQLite 3", "3.45.0", "Embedded relational persistence (users, profiles, history)"],
        ["Frontend UI Library", "React", "18.3.1", "Single Page Application (SPA) component architecture"],
        ["Build Tooling", "react-scripts / Node.js", "5.0.1 / 20.x", "Frontend compilation, bundling, and asset minification"]
    ]
    builder.add_table("Table 3.5: Software Dependencies and Technology Versions", headers_t35, data_t35,
                      col_widths=[Inches(1.5), Inches(1.8), Inches(1.1), Inches(2.8)])

    # 3.10 Detailed Use Case Specifications
    builder.add_h1("3.10 Comprehensive Use Case Specifications")
    builder.add_p(
        "To formally capture user interactions and system behavioral contracts, a detailed use case specification was developed for the "
        "primary consumer verification workflow. Table 3.6 documents Use Case UC-04: Multimodal Scanned Product Verification."
    )

    # Table 3.6: Use Case UC-04
    headers_t36 = ["Use Case Field", "Specification Details"]
    data_t36 = [
        ["Use Case Identifier", "UC-04: Multimodal Scanned Product Verification"],
        ["Primary Actor", "Authenticated Consumer / Mobile Shopper"],
        ["Pre-Conditions", "1. User is registered and logged in; 2. Dietary profile and allergen preferences configured."],
        ["Trigger", "Consumer captures or uploads a packaged food label image / barcode."],
        ["Main Success Scenario", "1. User initiates scan from ProductScanningView.\n2. System receives image and detects presence of barcode and/or label text.\n3. Pipeline A validates EAN-13 checksum and retrieves product metadata.\n4. Pipeline B assesses image quality, executes OpenCV Configuration B enhancement, extracts text via Tesseract, normalizes OCR typos, maps INS additives (750 taxonomy), and computes deterministic suitability score (0-100).\n5. System evaluates multimodal confidence vector.\n6. System renders AnalysisResultsView with score gauge, alerts, and additive details.\n7. System records transaction in SQLite analysis_history."],
        ["Alternative Flows", "4a. Low Image Quality: System detects blur (sigma < 70) or uneven lighting; applies adaptive thresholding.\n4b. Pipeline B Anomaly: OpenCV preprocessing throws exception; system executes automatic fallback to Configuration A.\n3a. Barcode Missing / Unlisted: System flags barcode status as 'not_provided' or 'lookup_failed'; Pipeline B completes autonomously."],
        ["Post-Conditions", "Consumer reviews verified suitability score, allergen alerts, and regulatory justifications; scan logged to history."]
    ]
    builder.add_table("Table 3.6: Detailed Use Case Specification: Scanned Product Verification", headers_t36, data_t36,
                      col_widths=[Inches(2.0), Inches(5.2)])

    print("Chapter 3 built successfully.")
