"""
chapter_4.py
Chapter 4: SYSTEM DESIGN AND ARCHITECTURAL MODELING
Revised for genuine academic originality, IEEE in-text citation linking,
and strict codebase fidelity.
"""

from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def build_chapter_4(builder):
    builder.add_chapter_title("4", "SYSTEM DESIGN AND ARCHITECTURAL MODELING")

    # 4.1 Architectural Philosophy
    builder.add_h1("4.1 Architectural Philosophy: Principles of Decoupled Multimodality")
    builder.add_p(
        "Software design for clinical and consumer food informatics must adhere to high standards of operational determinism, "
        "modularity, and explainability. Monolithic architectures—which couple barcode product identification directly to "
        "optical character recognition strings—suffer from structural fragility: when physical packaging curvature or ink bleed "
        "corrupts OCR extraction, the system either outputs false cross-source mismatch alarms or crashes silently. To eliminate "
        "these vulnerabilities, the proposed system is formulated around three architectural principles:\n\n"
        "1. Decoupled Pipeline Modularity: The architecture segregates product identity resolution (Pipeline A) from packaging text "
        "verification (Pipeline B). The two pipelines operate as independent analytical workflows that converge strictly at the presentation "
        "and audit layers.\n\n"
        "2. Deterministic Rule-Based Scoring: Dietary risk analysis is executed via deterministic mathematical deductions derived from "
        "statutory schedules (Codex Alimentarius [9], FSSAI [11], EFSA [13]). The system avoids opaque machine learning classifiers.\n\n"
        "3. Confidence-Aware Gating and Audit Logging: Every analytical stage produces an explicit confidence metric. These metrics "
        "synthesize into a 4-dimensional confidence vector that governs user notifications and triggers administrative triage for ambiguous tokens."
    )

    # 4.2 High-Level System Architecture and Workflow
    builder.add_h1("4.2 High-Level System Architecture and Workflow")
    builder.add_p(
        "The system is organized into a clean, multi-tier micro-service architecture comprising: the Presentation Layer (React 18 Single Page "
        "Application); the API Gateway Layer (Flask REST Server [28]); the Core Service Pipeline Layer (decoupled Barcode Service, "
        "OpenCV Preprocessing, Tesseract OCR, INS Taxonomy, Dietary Risk Engine, and HITL Audit subsystems); and the Persistence and "
        "Knowledge Layer (SQLite database [31], 750-entry INS taxonomy [9], and regulatory reference database)."
    )

    # Insert Figure 4.1
    builder.add_figure(
        "Figure 4.1: Overall Decoupled Multimodal System Architecture",
        "fig_4_1_decoupled_architecture.png",
        width_inches=4.8
    )

    builder.add_p(
        "As depicted in Figure 4.1, consumer interactions originate within the React frontend. HTTP requests bearing image payloads "
        "or barcode strings are transmitted via asynchronous AJAX calls to the Flask gateway [28]. The gateway validates request headers, "
        "enforces authentication bearer tokens [30], and routes payloads to the appropriate service pipelines. Analytical outputs are "
        "synthesized into a structured, unified JSON contract [29] and rendered on the client dashboard."
    )

    # 4.3 Pipeline A: Product Identification Subsystem Design
    builder.add_h1("4.3 Pipeline A: Product Identification Subsystem Design")
    builder.add_p(
        "Pipeline A is dedicated exclusively to resolving product identity from machine-readable optical barcodes. The subsystem "
        "is encapsulated in `backend/services/barcode_service.py`."
    )
    builder.add_p(
        "The operational lifecycle of Pipeline A follows a strictly sequential, fault-tolerant workflow:\n\n"
        "1. Image Ingestion and Bounding Box Detection: The decoder ingests raw image bytes, converts the frame to grayscale, and executes "
        "pattern recognition using pyzbar to locate standard linear barcode symbologies.\n\n"
        "2. Checksum Algorithm Verification: Once a 13-digit sequence is extracted, the service executes the mandatory Modulo-10 "
        "checksum algorithm [23]. Digits are split into odd- and even-positioned indices; weighted sums are computed; and the check digit "
        "is mathematically validated. If the checksum fails, the pipeline immediately halts external queries and flags the status as `invalid_checksum`.\n\n"
        "3. External REST Query: For mathematically valid codes, the service constructs an HTTP GET request to Open Food Facts [21] with a "
        "custom user-agent header. A strict 4.0-second socket timeout guard prevents network stalls.\n\n"
        "4. Offline Fallback Catalog: If the network socket times out, Open Food Facts returns HTTP 404, or the application operates "
        "in an isolated testing sandbox, Pipeline A queries its internal benchmark catalog, ensuring zero system crashes."
    )

    # Insert Figure 4.2
    builder.add_figure(
        "Figure 4.2: Pipeline A: Barcode Detection, Modulo-10 Validation & Catalog Lookup Flowchart",
        "fig_4_2_barcode_pipeline.png",
        width_inches=4.8
    )

    # 4.4 Pipeline B: Personalised Dietary Analysis Subsystem Design
    builder.add_h1("4.4 Pipeline B: Personalised Dietary Analysis Subsystem Design")
    builder.add_p(
        "Pipeline B represents the core scientific engine of the system, responsible for extracting physical ingredient text directly "
        "from packaging, identifying food additives, and evaluating consumer dietary compatibility. Encapsulated across "
        "`backend/services/ocr/image_preprocessor.py`, `backend/services/ocr/ocr_pipeline.py`, `backend/services/taxonomy_service.py`, "
        "and `backend/services/risk_engine.py`, Pipeline B executes independently of barcode availability."
    )

    # Insert Figure 4.3
    builder.add_figure(
        "Figure 4.3: Pipeline B: Personalised Dietary Label Analysis & Scoring Flowchart",
        "fig_4_3_ocr_pipeline.png",
        width_inches=4.8
    )

    builder.add_p(
        "As illustrated in Figure 4.3, packaging imagery is ingested, subjected to rigorous boundary checks, and routed through the "
        "dual-configuration optical engine. Following text extraction, the character stream undergoes regex extraction against the 750-entry "
        "INS taxonomy [9]. Extracted additives and raw text are concurrently evaluated by the dietary risk engine, which matches substances "
        "against user-configured presets and 11 regulated allergen categories, producing a deterministic suitability score from 0 to 100."
    )

    # 4.5 Optical Preprocessing Pipeline Design (Config A vs Config B)
    builder.add_h1("4.5 Optical Preprocessing Pipeline Design (Config A vs Config B)")
    builder.add_p(
        "A critical engineering contribution of this dissertation is the Dual-Configuration OCR Pipeline. To maintain backward compatibility "
        "and establish an unaugmented scientific baseline, the system implements Configuration A (Baseline Tesseract [2]). Concurrently, "
        "to overcome severe packaging distortions, it implements Configuration B (Enhanced OpenCV Pipeline [26])."
    )

    # Insert Figure 4.4 & Figure 4.5
    builder.add_figure(
        "Figure 4.4: Dual-Configuration OCR Architecture with Resilient Error Fallback",
        "fig_4_4_dual_ocr_architecture.png",
        width_inches=4.8
    )
    builder.add_figure(
        "Figure 4.5: OpenCV 8-Stage Image Enhancement Preprocessing Pipeline",
        "fig_4_5_opencv_enhancement_flow.png",
        width_inches=4.8
    )

    builder.add_p(
        "As detailed in Figure 4.4 and Figure 4.5, Configuration B executes eight specialized image processing stages:\n\n"
        "• Stage 1 (Validation & Safety Bounds): Rejects corrupt byte streams, enforces a memory ceiling, and downscales frames exceeding "
        "1800 px maximum dimension while strictly preserving the aspect ratio.\n\n"
        "• Stage 2 (Quality Grading & Blur Detection): Computes the variance of the Laplacian operator on the grayscale matrix. Frames with "
        "$\\text{Var}(\\nabla^2 I) < 100.0$ are classified as blurry, prompting controlled unsharp masking.\n\n"
        "• Stage 3 (Grayscale Normalization): Converts BGR channels to single-channel luminance intensity using ITU-R BT.601 weights.\n\n"
        "• Stage 4 (Bilateral Denoising): Applies non-linear bilateral filtering [6] ($d=9, \\sigma_{\\text{color}}=75, \\sigma_{\\text{space}}=75$) "
        "to smooth packaging background noise while preserving sharp font edge transitions.\n\n"
        "• Stage 5 (CLAHE Contrast Equalization): Applies Contrast-Limited Adaptive Histogram Equalization [5] with a clip limit of 2.5 and "
        "an $8 \\times 8$ grid, equalizing localized specular highlights on cellophane and metallic wrappers.\n\n"
        "• Stage 6 (Morphological Structuring): Deploys a $3 \\times 3$ rectangular structuring element to close minute gaps in broken character strokes.\n\n"
        "• Stage 7 (Adaptive Gaussian Thresholding): Applies adaptive Gaussian binarization [4], [7] to restore obscured characters across non-uniform lighting quadrants.\n\n"
        "• Stage 8 (Region Extraction & Deskewing): Isolates candidate text regions and aligns orientation prior to Tesseract OCR invocation.\n\n"
        "Crucially, if any exception occurs during Configuration B execution, the pipeline triggers an automatic, transparent fallback to "
        "Configuration A, ensuring continuous verification."
    )

    # 4.6 Frontend Component Hierarchy and State Management
    builder.add_h1("4.6 Frontend Component Hierarchy and State Management")
    builder.add_p(
        "The presentation tier is implemented as a React 18 Single Page Application (SPA) structured around a centralized state architecture. "
        "The root component manages global application state, including user authentication tokens, active dietary profiles, navigation "
        "indices, and persistent scan history caches. The component tree encapsulates `DashboardView`, `DietaryPreferencesView`, "
        "`AllergySelectionView`, `ProductScanningView`, `AnalysisResultsView`, `AnalysisHistoryView`, and `AuditQueueModal`."
    )

    # 4.7 Backend Micro-Service and REST API Design
    builder.add_h1("4.7 Backend Micro-Service and REST API Design")
    builder.add_p(
        "The backend server is engineered as a lightweight, stateless REST API hosted via Flask [28] on Python 3.10+. The API exposes "
        "modular endpoints categorized into functional controllers: Authentication (`/api/v1/auth/*`), Profile and Preferences "
        "(`/api/v1/profile/*`), Barcode Identification (`/api/v1/barcode/*`), OCR Operations (`/api/v1/ocr/*`), "
        "Core Analysis (`/api/v1/analyze`), and Audit & History (`/api/v1/audit/*`). CORS headers are enforced across "
        "all endpoints, and payloads follow standardized JSON contracts [29]."
    )

    # 4.8 Relational Database Architecture and Normalization
    builder.add_h1("4.8 Relational Database Architecture and Normalization")
    builder.add_p(
        "System data persistence is managed by an embedded SQLite 3 relational database [31] (`backend/data/app.db`). SQLite was selected "
        "for its zero-configuration footprint, serverless reliability, ACID transaction guarantees, and cross-platform portability. "
        "Relational integrity is enforced at the database engine level via `PRAGMA foreign_keys = ON;`."
    )
    builder.add_p(
        "The schema is strictly normalized to Third Normal Form (3NF), eliminating transitive dependencies and data anomalies. "
        "Tables 4.1 through 4.4 define the physical schema specifications for the core tables: `users`, `auth_tokens`, "
        "`dietary_profiles`, and `analysis_history`. Table 4.5 documents the indexing strategy utilized to optimize query performance."
    )

    # Table 4.1: users
    headers_t41 = ["Column Name", "Data Type", "Constraints", "Description"]
    data_t41 = [
        ["id", "INTEGER", "PRIMARY KEY AUTOINCREMENT", "Unique surrogate identifier for registered user."],
        ["username", "TEXT", "UNIQUE NOT NULL", "Alphanumeric unique login username."],
        ["email", "TEXT", "UNIQUE NOT NULL", "Unique email address for user communications."],
        ["password_hash", "TEXT", "NOT NULL", "Cryptographic PBKDF2-SHA256 password hash with salt [30]."],
        ["created_at", "TIMESTAMP", "DEFAULT CURRENT_TIMESTAMP", "Timestamp of initial account registration."],
        ["updated_at", "TIMESTAMP", "DEFAULT CURRENT_TIMESTAMP", "Timestamp of most recent profile modification."]
    ]
    builder.add_table("Table 4.1: Database Schema Specification: users Table", headers_t41, data_t41,
                      col_widths=[Inches(1.5), Inches(1.2), Inches(2.3), Inches(2.2)])

    # Table 4.2: auth_tokens
    headers_t42 = ["Column Name", "Data Type", "Constraints", "Description"]
    data_t42 = [
        ["token", "TEXT", "PRIMARY KEY", "Cryptographically random 64-char hexadecimal bearer token."],
        ["user_id", "INTEGER", "NOT NULL, FK -> users(id)", "Associated user reference (ON DELETE CASCADE)."],
        ["created_at", "TIMESTAMP", "DEFAULT CURRENT_TIMESTAMP", "Timestamp of token issuance."],
        ["expires_at", "TIMESTAMP", "NOT NULL", "Explicit token expiration timestamp (7-day validity)."]
    ]
    builder.add_table("Table 4.2: Database Schema Specification: auth_tokens Table", headers_t42, data_t42,
                      col_widths=[Inches(1.5), Inches(1.2), Inches(2.3), Inches(2.2)])

    # Table 4.3: dietary_profiles
    headers_t43 = ["Column Name", "Data Type", "Constraints", "Description"]
    data_t43 = [
        ["id", "INTEGER", "PRIMARY KEY AUTOINCREMENT", "Surrogate identifier for dietary profile."],
        ["user_id", "INTEGER", "UNIQUE NOT NULL, FK -> users(id)", "One-to-one user reference (ON DELETE CASCADE)."],
        ["preset_name", "TEXT", "DEFAULT 'custom'", "Active lifestyle preset (clean_eating, vegan, etc.)."],
        ["custom_override", "INTEGER", "DEFAULT 0", "Boolean flag indicating manual deviation from preset."],
        ["avoid_synthetic_colors", "INTEGER", "DEFAULT 0", "Boolean flag to penalize synthetic food dyes."],
        ["avoid_preservatives", "INTEGER", "DEFAULT 0", "Boolean flag to penalize chemical preservatives."],
        ["avoid_artificial_sweeteners", "INTEGER", "DEFAULT 0", "Boolean flag to penalize intense artificial sweeteners."],
        ["avoid_msg_flavor_enhancers", "INTEGER", "DEFAULT 0", "Boolean flag to penalize glutamates and inosinates."],
        ["avoid_animal_derivatives", "INTEGER", "DEFAULT 0", "Boolean flag to penalize animal-derived additives."],
        ["custom_allergens", "TEXT", "DEFAULT '[]'", "JSON array of selected user allergen strings."],
        ["custom_avoid_ins", "TEXT", "DEFAULT '[]'", "JSON array of specific INS codes strictly avoided."],
        ["custom_caution_ins", "TEXT", "DEFAULT '[]'", "JSON array of specific INS codes flagged for caution."]
    ]
    builder.add_table("Table 4.3: Database Schema Specification: dietary_profiles Table", headers_t43, data_t43,
                      col_widths=[Inches(1.8), Inches(1.1), Inches(2.2), Inches(2.1)])

    # Table 4.4: analysis_history
    headers_t44 = ["Column Name", "Data Type", "Constraints", "Description"]
    data_t44 = [
        ["id", "INTEGER", "PRIMARY KEY AUTOINCREMENT", "Unique surrogate identifier for scan record."],
        ["user_id", "INTEGER", "FK -> users(id)", "User reference (ON DELETE SET NULL for guest tracking)."],
        ["session_id", "TEXT", "NULLABLE", "Transient session token for unauthenticated guest scans."],
        ["ean", "TEXT", "NULLABLE", "Scanned or entered 13-digit EAN barcode string [23]."],
        ["product_name", "TEXT", "NULLABLE", "Resolved or default product display name."],
        ["raw_text", "TEXT", "NULLABLE", "Truncated raw OCR extracted ingredient text."],
        ["ocr_confidence", "REAL", "DEFAULT 1.0", "Mean word-level Tesseract character confidence (0-1)."],
        ["final_score", "INTEGER", "NULLABLE", "Universal baseline safety score (0-100)."],
        ["grade", "TEXT", "NULLABLE", "Universal baseline grade letter ('A' to 'E')."],
        ["personal_score", "INTEGER", "NULLABLE", "Personalised dietary suitability score (0-100)."],
        ["personal_verdict", "TEXT", "NULLABLE", "Personalised compatibility verdict string."],
        ["allergen_alerts", "TEXT", "DEFAULT '[]'", "JSON array of detected allergen alert objects."],
        ["additives_summary", "TEXT", "DEFAULT '[]'", "JSON array of detected INS codes [9]."],
        ["system_audit_summary", "TEXT", "DEFAULT '{}'", "JSON object containing multimodal confidence vector."],
        ["scanned_at", "TIMESTAMP", "DEFAULT CURRENT_TIMESTAMP", "Timestamp of scan completion."]
    ]
    builder.add_table("Table 4.4: Database Schema Specification: analysis_history Table", headers_t44, data_t44,
                      col_widths=[Inches(1.6), Inches(1.1), Inches(2.2), Inches(2.3)])

    # Table 4.5: Indexes
    headers_t45 = ["Index Identifier", "Target Table", "Indexed Columns", "Optimization Objective"]
    data_t45 = [
        ["idx_users_username", "users", "username", "Enforces unique constraint and speeds up login lookups."],
        ["idx_users_email", "users", "email", "Accelerates duplicate email verification during registration."],
        ["idx_tokens_token", "auth_tokens", "token", "Enables constant-time O(1) session token validation."],
        ["idx_tokens_user", "auth_tokens", "user_id", "Accelerates session invalidation on user logout."],
        ["idx_profiles_user", "dietary_profiles", "user_id", "Optimizes 1-to-1 profile retrieval during analysis requests."],
        ["idx_history_user", "analysis_history", "user_id", "Optimizes user scan history pagination and filtering."],
        ["idx_history_ean", "analysis_history", "ean", "Enables rapid historical lookups by product barcode."]
    ]
    builder.add_table("Table 4.5: Database Indexing Catalog for Query Optimization", headers_t45, data_t45,
                      col_widths=[Inches(1.8), Inches(1.3), Inches(1.5), Inches(2.6)])

    # 4.9 UML Structural and Behavioral Models
    builder.add_h1("4.9 Unified Modeling Language (UML) Structural and Behavioral Models")
    builder.add_p(
        "To provide a standard engineering specification of system behavior and component interactions, formal "
        "Unified Modeling Language (UML) diagrams and structured Data Flow Diagrams (DFDs) were developed based directly "
        "on the verified source code."
    )

    # 4.9.1 Use Case Diagram
    builder.add_h2("4.9.1 System Use Case Diagram")
    builder.add_p(
        "The Use Case Diagram defines the operational interactions between external actors and system boundaries. Two primary "
        "actors interact with the system: the Consumer / Mobile User, who executes scans, configures profiles, and reviews "
        "history; and the Quality Auditor / Admin, who monitors the Human-in-the-Loop review queue and refines additive mappings."
    )
    builder.add_figure("Figure 4.6: UML Use Case Diagram of Food Label Verification System", "fig_4_6_use_case_diagram.png", width_inches=4.8)

    # 4.9.2 Data Flow Diagrams (DFD)
    builder.add_h2("4.9.2 Data Flow Diagrams (Level 0, Level 1, Level 2)")
    builder.add_p(
        "Data Flow Diagrams model the transformation of information as it traverses input interfaces, algorithmic processes, "
        "relational data stores, and external service entities. Figure 4.7 presents the Level-0 Context Diagram, showing macroscopic "
        "data flows between the consumer, the system boundary, Open Food Facts [21], and the auditor console."
    )
    builder.add_figure("Figure 4.7: Level-0 Context Data Flow Diagram (DFD)", "fig_4_7_dfd_level0.png", width_inches=4.8)

    builder.add_p(
        "Figure 4.8 presents the Level-1 Data Flow Diagram, decomposing the system into five primary functional processes: User & "
        "Profile Management (1.0), Barcode Validation & Identity Retrieval (2.0), Image Preprocessing & OCR Extraction (3.0), Additive "
        "Taxonomy & INS Classification (4.0), and Dietary Matching & Suitability Scoring (5.0), mapped to three physical data stores."
    )
    builder.add_figure("Figure 4.8: Level-1 Data Flow Diagram (DFD) of Major Subsystems", "fig_4_8_dfd_level1.png", width_inches=4.8)

    builder.add_p(
        "Figure 4.9 delivers the Level-2 Detailed DFD focusing on Process 5.0 (Personalised Dietary Scoring), tracking text through "
        "OCR Typo Normalization (5.1), Regex Codex Token Extraction (5.2), Allergen Keyword Scanning (5.3), and Mathematical "
        "Rule Deduction Scoring (5.4)."
    )
    builder.add_figure("Figure 4.9: Level-2 Detailed DFD for Additive Extraction and Personalised Scoring", "fig_4_9_dfd_level2.png", width_inches=4.8)

    # 4.9.3 Entity-Relationship Diagram
    builder.add_h2("4.9.3 Entity-Relationship (ER) Diagram")
    builder.add_p(
        "Figure 4.10 illustrates the complete Entity-Relationship diagram for the relational database schema, detailing primary keys, "
        "foreign key constraints, column cardinalities, and relationship types across `users`, `auth_tokens`, `dietary_profiles`, "
        "and `analysis_history` [31]."
    )
    builder.add_figure("Figure 4.10: Relational Database Entity-Relationship (ER) Schema Diagram", "fig_4_10_er_diagram.png", width_inches=4.8)

    # 4.9.4 Sequence Diagrams
    builder.add_h2("4.9.4 System Sequence Diagrams")
    builder.add_p(
        "Sequence diagrams capture the chronological exchange of asynchronous messages, function invocations, and HTTP responses "
        "between system lifelines. Figure 4.11 documents the execution lifecycle for Pipeline A (Barcode Product Identification)."
    )
    builder.add_figure("Figure 4.11: Sequence Diagram: Barcode Detection and External Verification", "fig_4_11_sequence_barcode.png", width_inches=4.8)

    builder.add_p(
        "Figure 4.12 documents the sequence lifecycle for Pipeline B (Dietary Label Analysis and Scoring), tracking asynchronous "
        "calls across the client SPA, API Gateway, OpenCV Preprocessing pipeline [26], INS Parser [9], Risk Engine, and SQLite logging."
    )
    builder.add_figure("Figure 4.12: Sequence Diagram: Personalised Dietary Label Analysis and Scoring", "fig_4_12_sequence_ocr.png", width_inches=4.8)

    # 4.9.5 Activity and Deployment Diagrams
    builder.add_h2("4.9.5 Activity and Deployment Diagrams")
    builder.add_p(
        "Figure 4.13 presents the UML Activity Diagram modeling the operational decision nodes of the Human-in-the-Loop audit queue. "
        "When confidence falls below 0.60 or unmapped chemical tokens appear, the workflow branches automatically into the audit queue."
    )
    builder.add_figure("Figure 4.13: Activity Diagram: Human-in-the-Loop (HITL) Audit Workflow", "fig_4_13_activity_audit.png", width_inches=4.8)

    builder.add_p(
        "Figure 4.14 illustrates the physical deployment topology, detailing the client browser execution tier, the Flask/OpenCV/Tesseract "
        "application server container, and external HTTPS connections to Open Food Facts [21] and regulatory data registries."
    )
    builder.add_figure("Figure 4.14: Physical Deployment and Component Topology", "fig_4_14_deployment_diagram.png", width_inches=4.8)

    print("Chapter 4 built successfully.")
