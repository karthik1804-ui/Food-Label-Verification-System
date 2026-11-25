"""
chapter_1.py
Chapter 1: INTRODUCTION
Revised for genuine academic originality, IEEE in-text citation linking,
and strict codebase fidelity.
"""

import docx
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def build_chapter_1(builder):
    # Transition to Part B (New Section with Arabic Numerals starting at 1)
    doc = builder.doc
    section2 = doc.add_section(docx.enum.section.WD_SECTION.NEW_PAGE)
    builder.configure_section_margins(section2, is_part_a=False)

    builder.add_chapter_title("1", "INTRODUCTION")

    # 1.1 Background of Packaged Food Labeling
    builder.add_h1("1.1 Background of Packaged Food Labeling")
    builder.add_p(
        "Commercial food retail relies extensively on industrially packaged foodstuffs that incorporate a broad spectrum "
        "of chemical and biochemical additives. Preservatives, colorants, emulsifying stabilizers, artificial intense "
        "sweeteners, and texture modifiers are systematically deployed across global supply chains to inhibit microbiological "
        "spoilage, standardize sensory attributes, and extend shelf life across distant distribution channels. While these "
        "substances fulfill critical logistics and preservation roles, their widespread adoption presents acute health and "
        "transparency challenges for consumers navigating specific medical intolerances, immunological allergies, or lifestyle constraints."
    )
    builder.add_p(
        "To establish international standards for consumer protection, the Codex Alimentarius Commission—administered jointly "
        "by the Food and Agriculture Organization (FAO) and the World Health Organization (WHO)—promulgated global labeling "
        "standards [9], [10]. In India, the Food Safety and Standards Authority of India (FSSAI) enforces the Food Safety and "
        "Standards (Food Products Standards and Food Additives) Regulations [11] alongside the Food Safety and Standards "
        "(Labelling and Display) Regulations [12]. Corresponding regulatory mandates are enforced by the European Food Safety "
        "Authority (EFSA) under Regulation (EC) No 1333/2008 [13] and the United States Food and Drug Administration (FDA)."
    )
    builder.add_p(
        "Despite statutory disclosure requirements, the practical utility of packaged food labels for shoppers remains severely "
        "constrained. Packaging typography is frequently compressed into microscopic kerning (often 4.5 to 6 points), rendered in "
        "low-contrast inks across reflective cellophane or curved metallic surfaces, and expressed via cryptic numerical nomenclature. "
        "Consequently, there exists an operational disconnect between statutory compliance on packaging and the cognitive ability "
        "of consumers to identify potentially hazardous substances at the point of purchase."
    )

    # 1.2 Evolution of Food Additive Regulation & International Standards
    builder.add_h1("1.2 Evolution of Food Additive Regulation & International Standards")
    builder.add_p(
        "To standardize additive declarations across multilingual trade environments, the Codex Alimentarius Commission established "
        "the International Numbering System for Food Additives (INS) under Standard CXG 36-1989 [9]. Under this codification, each "
        "approved substance is assigned a discrete numerical identifier, optionally paired with alphabetical or lower-case Roman "
        "suffixes to denote distinct chemical salts (for instance, INS 500(i) for Sodium Carbonate versus INS 500(ii) for Sodium "
        "Hydrogen Carbonate)."
    )
    builder.add_p(
        "In the European Union, this hierarchy was codified under the 'E-number' convention [13], establishing functional class series: "
        "the 100 series for food colorants; the 200 series for antimicrobial preservatives; the 300 series for antioxidants and acidity "
        "regulators; the 400 series for thickeners and emulsifiers; the 500 series for anti-caking agents and pH buffers; the 600 series "
        "for flavor enhancers; the 700 series for technical processing aids; and the 900 series for intense artificial sweeteners and glazing agents."
    )
    builder.add_p(
        "In India, FSSAI regulations [11] permit manufacturers to declare additives by either their generic functional title accompanied "
        "by the INS number or by their formal chemical title. Commercial packaging predominantly deploys the numerical shorthand "
        "(e.g., 'Preservative (INS 211)' rather than 'Sodium Benzoate'). This practice obscures the common chemical identity behind an "
        "abstract numerical label, preventing sensitized consumers from recognizing additives they have been clinically advised to avoid."
    )

    # 1.3 Modern Consumer Health Challenges (Allergens, Lifestyle Diets)
    builder.add_h1("1.3 Modern Consumer Health Challenges (Allergens, Lifestyle Diets)")
    builder.add_p(
        "The prevalence of chemical food additives coincides with an escalating clinical incidence of food hypersensitivity, "
        "immunogenic allergies, and metabolic intolerances. Immunological food allergies affect an estimated 6% to 8% of pediatric "
        "populations and 3% to 4% of adults worldwide. Ingestion of specific allergen proteins—such as gluten in celiac pathology, "
        "arachin in peanut allergies, or casein in dairy intolerance—can induce severe physiological reactions ranging from acute "
        "gastrointestinal inflammation to life-threatening systemic anaphylaxis."
    )
    builder.add_p(
        "Beyond classic protein allergens, rigorous toxicological research has linked specific chemical additives to behavioral and "
        "inflammatory reactions. A prominent example is the randomized double-blind clinical trial conducted by McCann et al. [15], "
        "which established that mixtures of artificial azo dyes—Tartrazine (INS 102), Sunset Yellow FCF (INS 110), Carmoisine (INS 122), "
        "Ponceau 4R (INS 124), Allura Red AC (INS 129), and Quinoline Yellow (INS 104)—administered with the preservative Sodium Benzoate "
        "(INS 211) significantly increase hyperactive behaviors in children. These findings prompted extensive EFSA reviews [14] and "
        "led to mandatory European warning labels under Regulation (EC) No 1333/2008 [13]."
    )
    builder.add_p(
        "Simultaneously, increasing segments of the consumer population maintain strict ethical or religious dietary standards, "
        "such as strict veganism, vegetarianism, or religious dietary codes. In many packaged foods, additives conceal animal-derived "
        "origins: Carmine (INS 120) is an intense crimson pigment derived from dried cochineal insects (*Dactylopius coccus*); "
        "Gelatin (INS 428) is extracted from bovine or porcine collagen; and L-Cysteine (INS 920), deployed as an industrial dough "
        "conditioner, is frequently synthesized from animal bristles or poultry feathers. Consumers cannot deduce these origins from the "
        "abstract INS code alone."
    )

    # Insert Figure 1.1
    builder.add_figure(
        "Figure 1.1: Growth of Food Additive Market vs. Consumer Sensitivities (2016–2027)",
        "fig_1_1_additive_trends.png",
        width_inches=4.8
    )

    # 1.4 Problem Statement: The Gap in Automated Label Verification
    builder.add_h1("1.4 Problem Statement: The Gap in Automated Label Verification")
    builder.add_p(
        "Automated mobile assistance has emerged as a viable avenue to assist consumers at the point of sale. However, existing "
        "commercial applications and prior academic systems suffer from architectural and algorithmic limitations that undermine their reliability."
    )
    builder.add_p(
        "The core technical problem spans four distinct failure modes:\n\n"
        "1. Vulnerability of Barcode-Only Lookups: Applications like Yuka or Open Food Facts mobile rely on optical EAN-13 barcodes [23] "
        "to query crowd-sourced registries [21]. While fast, barcode queries decouple verification from the physical container. When food "
        "manufacturers reformulate products—substituting ingredients or introducing novel additives without changing the Global Trade Item "
        "Number (GTIN)—the database returns outdated ingredient lists, creating severe hazards for allergic individuals.\n\n"
        "2. Monolithic OCR Collapse on Curved Substrates: Academic vision approaches frequently pass uncurated packaging images into baseline "
        "OCR engines like Tesseract [2], [3]. On cylindrical packaging (beverage cans, jars), cellophane wrappers, and uneven retail lighting, "
        "raw Character Error Rates (CER) escalate sharply, causing critical INS numeric codes and comma delimiters to be corrupted.\n\n"
        "3. Unexplainable Black-Box ML Claims: Recent academic efforts, such as Rawat et al. (IEEE ICCCA 2025) [1], pass uncurated OCR text "
        "directly into supervised machine learning classifiers to predict binary 'healthy' versus 'unhealthy' outcomes. Such models are "
        "inherently unexplainable, fail to provide clinical ingredient attribution, and risk severe errors by attempting statistical predictions "
        "on noisy character data instead of applying deterministic statutory rules.\n\n"
        "4. Absence of Confidence Gating and Human Review: Contemporary systems silently guess when optical recognition confidence degrades, "
        "lacking confidence-aware metrics to quantify optical clarity and route ambiguous chemical tokens to administrative audit."
    )

    # 1.5 Research Motivation and Social Significance
    builder.add_h1("1.5 Research Motivation and Social Significance")
    builder.add_p(
        "This research is motivated by the necessity of bridging regulatory food chemistry and consumer point-of-sale decision making. "
        "Statutory food disclosure laws fail to achieve their protective intent if consumers cannot interpret cryptic chemical designations "
        "under time-constrained retail conditions."
    )
    builder.add_p(
        "By engineering a confidence-aware verification framework, this investigation provides a practical tool for populations managing "
        "celiac disease, acute allergen sensitivities, pediatric dietary restrictions, diabetic sweeteners, or ethical vegan diets. "
        "The system operates with high transparency, explaining the precise regulatory rationale for every flagged substance."
    )
    builder.add_p(
        "Furthermore, this dissertation establishes an auditable engineering methodology: enforcing architectural decoupling between "
        "modalities, replacing black-box classifiers with transparent statutory rule deductions, and integrating an active Human-in-the-Loop "
        "(HITL) audit queue for unresolved chemical nomenclature."
    )

    # 1.6 Project Objectives (Primary & Secondary)
    builder.add_h1("1.6 Project Objectives (Primary & Secondary)")
    builder.add_p(
        "To overcome the identified limitations, the investigation was organized around nine specific technical objectives."
    )

    # Table 1.1: Objectives
    headers_t11 = ["Objective ID", "Classification", "Specific Technical Objective Description", "Target Module"]
    data_t11 = [
        ["OBJ-01", "Primary", "Design and implement an automated EAN-13 barcode detection, decoding, and Modulo-10 checksum validation pipeline with external REST database lookup.", "Barcode Service (`backend/services/barcode_service.py`)"],
        ["OBJ-02", "Primary", "Engineer an 8-stage adaptive OpenCV image preprocessing pipeline (Configuration B) to overcome packaging curvature, blur, specular reflections, and uneven illumination.", "Optical Preprocessor (`backend/services/ocr/image_preprocessor.py`)"],
        ["OBJ-03", "Primary", "Preserve baseline Configuration A intact and implement resilient automatic error fallback from Configuration B to Configuration A on processing anomalies.", "OCR Pipeline (`backend/services/ocr/ocr_pipeline.py`)"],
        ["OBJ-04", "Primary", "Construct an authoritative local food additive taxonomy comprising 750 verified INS and E-number substances mapped across 7 functional classes with official regulatory citations.", "Taxonomy Engine (`backend/data/ins_taxonomy.json`)"],
        ["OBJ-05", "Primary", "Implement a deterministic, rule-based dietary risk engine that calculates personalized suitability scores (0-100) with explicit mathematical deductions.", "Dietary Risk Engine (`backend/services/risk_engine.py`)"],
        ["OBJ-06", "Secondary", "Formulate a 4-dimensional multimodal confidence vector evaluating optical clarity, taxonomy resolution, barcode status, and product identity certainty.", "Audit Subsystem (`backend/services/audit_service.py`)"],
        ["OBJ-07", "Secondary", "Implement a Human-in-the-Loop (HITL) audit queue enabling authorized reviewers to confirm, correct, or reject unmapped chemical candidate strings.", "HITL Review Modal (`frontend/src/components/AuditQueueModal.jsx`)"],
        ["OBJ-08", "Secondary", "Design a responsive Minimalist Health-Tech user interface (React 18 SPA) delivering high-contrast, uncluttered consumer dashboards.", "Frontend (`frontend/src/`)"],
        ["OBJ-09", "Secondary", "Achieve 100% verification across a comprehensive automated test suite spanning unit, integration, boundary, and regression assertions (187 test cases).", "Test Suite (`tests/`)"]
    ]
    builder.add_table("Table 1.1: Primary and Secondary Objectives of the Investigation", headers_t11, data_t11,
                      col_widths=[Inches(1.0), Inches(1.1), Inches(3.4), Inches(1.5)])

    # 1.7 Scope and Operational Constraints (Decoupled Pipelines)
    builder.add_h1("1.7 Scope and Operational Constraints (Decoupled Pipelines)")
    builder.add_p(
        "To ensure methodological integrity and prevent spurious mismatch alerts, explicit boundaries were established:\n\n"
        "1. Decoupled Analytical Modalities: The operational scope maintains a strict functional separation between product metadata "
        "retrieval (Pipeline A) and physical packaging text verification (Pipeline B). The system deliberately avoids automated, "
        "character-by-character reconciliations between OCR extractions and remote database records. Real-world consumer containers "
        "frequently present geometric curvature, printing ink bleed, and local brand reformulation differences; forcing an automated "
        "cross-source match invariably generates false-positive conflict notifications that confuse the consumer. Consequently, "
        "barcode data provides complementary historical context, while OCR evaluates the physical item in hand.\n\n"
        "2. Deterministic Mathematical Scoring: Food suitability scoring operates strictly on deterministic mathematical deductions "
        "derived from authoritative regulatory statutes (Codex, FSSAI, EFSA). The system avoids black-box machine learning classifiers "
        "or unverified predictive ratings.\n\n"
        "3. Informational Verification Boundary: The software is engineered as a consumer informational assistance tool. It does not "
        "constitute a medical diagnostic device, clinical food safety certification, or legal warranty against industrial cross-contamination."
    )

    # 1.8 Proposed Multimodal Engineering Methodology
    builder.add_h1("1.8 Proposed Multimodal Engineering Methodology")
    builder.add_p(
        "The system bifurcates the verification workflow into two independent, concurrent processing streams that converge exclusively "
        "at the presentation and audit layers."
    )
    builder.add_p(
        "Pipeline A processes barcode imagery by identifying the bounding box, executing zbar decoding, and verifying data integrity "
        "via the Modulo-10 checksum algorithm [23]. Upon validation, it queries Open Food Facts [21], with automatic fallback to a "
        "curated local catalog during network latency or offline scenarios.\n\n"
        "Simultaneously, Pipeline B handles packaging label imagery using a dual-configuration optical engine. Configuration B executes "
        "an 8-stage OpenCV image enhancement workflow to stabilize contrast and remove blur before invoking Tesseract OCR [2], [3]. "
        "The extracted text stream undergoes regex normalization to correct optical misreads within numeric bounds, filtered against "
        "Codex Alimentarius ranges (100–1599) [9], and cross-referenced with the 750-entry INS taxonomy. The dietary risk engine computes "
        "deterministic score deductions and formulates a 4-dimensional confidence vector to govern audit logging."
    )

    # Insert Figure 1.2
    builder.add_figure(
        "Figure 1.2: Decoupled Multimodal Verification Methodology",
        "fig_1_2_decoupled_methodology.png",
        width_inches=4.8
    )

    # 1.9 Organization and Structure of the Report
    builder.add_h1("1.9 Organization and Structure of the Report")
    builder.add_p(
        "The remainder of this dissertation is organized into six technical chapters, followed by academic references and "
        "institutional documentation:\n\n"
        "• Chapter 2 – Literature Survey: Reviews prior research in optical character recognition, computer vision image preprocessing, "
        "barcode standards, and nutritional decision support. Delivers a critical comparative critique of the baseline study by "
        "Rawat et al. (IEEE ICCCA 2025) [1] and establishes identified research gaps.\n\n"
        "• Chapter 3 – System Requirements and Analysis: Evaluates existing system limitations, specifies functional and non-functional "
        "requirements, presents feasibility analysis, and details mathematical models for image enhancement and confidence scoring.\n\n"
        "• Chapter 4 – System Design and Architectural Modeling: Expounds the decoupled architecture, dual-pipeline design, relational "
        "database schema, and comprehensive UML models (DFDs, ER, Sequence, Activity, State, and Deployment diagrams).\n\n"
        "• Chapter 5 – System Implementation: Documents the concrete software implementation across Flask micro-services, OpenCV preprocessing "
        "stages, Tesseract configuration, 750-entry INS taxonomy algorithms, rule-based deduction formulas, HITL audit queue workflows, "
        "and React 18 UI components.\n\n"
        "• Chapter 6 – Testing, Verification, and Performance Evaluation: Details the quality assurance framework, boundary condition "
        "testing, barcode verification logs, latency benchmarking, and the complete execution breakdown of all 187 automated passing tests.\n\n"
        "• Chapter 7 – Conclusion and Future Enhancements: Summarizes project achievements, highlights contributions to academic food "
        "informatics, articulates technical limitations, and charts prospective research avenues.\n\n"
        "• References: Compiles comprehensive IEEE-style academic citations covering peer-reviewed literature and statutory regulations.\n\n"
        "• Part C: Encompasses research paper publication details and professional placement documentation placeholders."
    )

    print("Chapter 1 built successfully.")
