"""
chapter_1.py
Chapter 1: INTRODUCTION
Generates full academic prose, tables, and figures for Chapter 1.
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
        "The modern retail food landscape has undergone a profound transformation over the past five decades, shifting from "
        "minimally processed, locally sourced whole commodities toward ultra-processed, industrially packaged foodstuffs. "
        "In industrialized and emerging economies alike, packaged food products constitute the dominant proportion of daily "
        "caloric intake. This massive industrialization has necessitated the widespread adoption of synthetic and natural "
        "food additives, including antimicrobial preservatives, synthetic colorants, artificial intense sweeteners, emulsifying "
        "stabilizers, texturizers, and chemical flavor enhancers. While these technological substances ensure shelf-life "
        "stability across extended global supply chains, maintain microbiological safety against foodborne pathogens, and "
        "impart standardized sensory attributes, they simultaneously introduce significant public health, dietary, and "
        "regulatory challenges for consumers."
    )
    builder.add_p(
        "To safeguard consumer sovereignty and public welfare, international food governance bodies—most notably the Codex "
        "Alimentarius Commission established jointly by the Food and Agriculture Organization (FAO) and the World Health "
        "Organization (WHO)—promulgated standardized statutory labeling codes. In India, the Food Safety and Standards "
        "Authority of India (FSSAI) enforces the Food Safety and Standards (Packaging and Labelling) Regulations, mandating "
        "comprehensive disclosure of ingredient lists, allergen declarations, nutritional facts, manufacturing dates, and "
        "additive identifiers. Parallel statutory mandates are enforced by the European Food Safety Authority (EFSA) within the "
        "European Union and the United States Food and Drug Administration (FDA)."
    )
    builder.add_p(
        "Despite these stringent regulatory mandates, the practical utility of food package labeling for ordinary consumers "
        "remains severely impaired. Packaged labels are routinely formatted with microscopic typography (often as small as "
        "4.5 to 6 points), compressed kerning, low-contrast ink formulations printed on reflective metallic or cellophane foils, "
        "and convoluted scientific nomenclatures that confound non-expert readers. Consequently, a substantial communication "
        "chasm exists between the legal presence of ingredient disclosures and the cognitive comprehension of the individuals "
        "purchasing and consuming these products."
    )

    # 1.2 Evolution of Food Additive Regulation & International Standards
    builder.add_h1("1.2 Evolution of Food Additive Regulation & International Standards")
    builder.add_p(
        "Historically, food adulteration and unregulated chemical usage posed severe threats to public health during the Industrial "
        "Revolution, prompting the creation of systematic additive codification frameworks. To eliminate linguistic barriers "
        "in cross-border commodity trade and establish clear toxicological thresholds, the Codex Alimentarius Commission "
        "instituted the International Numbering System for Food Additives (INS). Under this numerical standard, every permitted "
        "substance is assigned a unique three- or four-digit identification code, optionally suffixed with lower-case Roman "
        "numerals or alphabetic qualifiers to distinguish specific chemical sub-forms (for instance, INS 500(i) for Sodium "
        "Carbonate versus INS 500(ii) for Sodium Hydrogen Carbonate)."
    )
    builder.add_p(
        "Within the European Union, this numbering framework was formally adopted under the 'E-number' schema, wherein the "
        "prefix 'E' denotes European approval following safety assessment. The numbering hierarchy is organized into discrete "
        "functional series: the 100 series encompasses food colorants; the 200 series comprises chemical preservatives and "
        "antimicrobial agents; the 300 series covers antioxidants and acidity regulators; the 400 series designates thickeners, "
        "stabilizers, and emulsifiers; the 500 series specifies pH regulators and anti-caking agents; the 600 series isolates "
        "flavor enhancers such as glutamates and inosinates; the 700 series encompasses technical processing aids and antibiotics; "
        "and the 900 series isolates intense artificial sweeteners, glazing agents, and packaging gases."
    )
    builder.add_p(
        "In India, FSSAI adopted the INS numbering convention under the Food Safety and Standards (Food Products Standards "
        "and Food Additives) Regulations, 2011. While manufacturers are permitted to declare additives by either their generic "
        "functional class accompanied by the INS number or their full chemical nomenclature, commercial brands overwhelmingly "
        "favor the numerical shorthand (e.g., 'Preservative (INS 211)' or 'Colour (102)'). This practice conceals the commonly "
        "understood substance name (e.g., Sodium Benzoate or Tartrazine) behind abstract numbering, preventing consumers from "
        "recognizing substances they have been clinically advised to avoid."
    )

    # 1.3 Modern Consumer Health Challenges (Allergens, Lifestyle Diets)
    builder.add_h1("1.3 Modern Consumer Health Challenges (Allergens, Lifestyle Diets)")
    builder.add_p(
        "The ubiquity of chemical additives intersects critically with an unprecedented epidemiological surge in chronic health "
        "conditions, immunogenic food allergies, dietary intolerances, and ethical lifestyle commitments. Food hypersensitivity "
        "is recognized globally as a escalating public health concern, affecting approximately 6% to 8% of children and 3% to 4% "
        "of the adult population worldwide, with clinical prevalence exhibiting steep upward trajectories in urban demographics. "
        "For sensitized individuals, involuntary ingestion of specific allergen proteins—such as gluten in celiac disease, "
        "arachin and conarachin in peanut allergies, ovalbumin in egg hypersensitivity, or casein in dairy intolerances—can "
        "precipitate severe physiological distress ranging from atopic dermatitis and acute gastrointestinal dysfunction to "
        "life-threatening anaphylaxis."
    )
    builder.add_p(
        "Beyond classical immunological allergens, extensive epidemiological and clinical toxicological literature has "
        "implicated specific chemical additives in adverse physiological reactions. A prominent example is the landmark "
        "Southampton randomized double-blind crossover study, which demonstrated that mixtures of certain synthetic azo "
        "food colors—specifically Tartrazine (INS 102), Sunset Yellow FCF (INS 110), Carmoisine (INS 122), Ponceau 4R (INS 124), "
        "Allura Red AC (INS 129), and Quinoline Yellow (INS 104)—combined with the chemical preservative Sodium Benzoate (INS 211), "
        "provoke heightened hyperactivity and attention deficit behavior in children. Consequently, the European Parliament enacted "
        "Regulation (EC) No 1333/2008, mandating that food products containing any of the 'Southampton Six' colorants carry the "
        "mandatory warning label: 'May have an adverse effect on activity and attention in children'."
    )
    builder.add_p(
        "Simultaneously, increasing segments of the global population adhere to ethical, philosophical, or religious dietary "
        "regimens, including strict veganism, vegetarianism, clean-eating lifestyles, and additive-restricted regimens for infants "
        "and pediatric care. In many instances, chemical additives conceal covert animal-derived origins that compromise vegan "
        "or religious commitments. For example, Carmine / Cochineal (INS 120) is an intense red pigment derived by crushing "
        "dried female cochineal insects (*Dactylopius coccus*); Gelatin (INS 428) is extracted through prolonged boiling of bovine "
        "or porcine skin and bone collagen; and L-Cysteine (INS 920), utilized as a flour treatment agent in industrial baking, "
        "is frequently synthesized from animal bristles or duck feathers. Consumers cannot readily identify these animal origins "
        "from the abstract INS code alone."
    )

    # Insert Figure 1.1
    builder.add_figure(
        "Figure 1.1: Growth of Food Additive Market vs. Consumer Sensitivities (2016–2027)",
        "fig_1_1_additive_trends.png",
        width_inches=4.0
    )

    # 1.4 Problem Statement: The Gap in Automated Label Verification
    builder.add_h1("1.4 Problem Statement: The Gap in Automated Label Verification")
    builder.add_p(
        "Automated mobile and computing assistance has emerged as a promising avenue to empower consumers during point-of-sale "
        "purchasing decisions. However, contemporary commercial and academic solutions suffer from fundamental architectural and "
        "algorithmic shortcomings that render them inadequate for reliable packaged food verification."
    )
    builder.add_p(
        "The fundamental problem can be formally defined across four distinct operational dimensions:\n\n"
        "1. Vulnerability of Barcode-Only Applications: Popular consumer applications rely almost exclusively on scanning the "
        "EAN-13 or UPC barcode printed on packaging, querying crowd-sourced databases such as Open Food Facts or proprietary "
        "commercial registries. While computationally instantaneous, barcode-only systems decouple verification from the actual "
        "physical product in the consumer's hand. When manufacturers reformulate food products—substituting ingredients, introducing "
        "novel preservatives, or altering allergen profiles without updating the registered Global Trade Item Number (GTIN)—the "
        "barcode query returns obsolete historical metadata, exposing allergic consumers to severe health risks.\n\n"
        "2. Monolithic Verification Failure on Curved Surfaces: Academic attempts to deploy computer vision and Optical Character "
        "Recognition (OCR) directly onto packaging labels typically employ monolithic, single-pass OCR engines (such as baseline "
        "Tesseract or generic cloud APIs). These models suffer severe accuracy collapse when presented with real-world consumer "
        "images characterized by cylindrical package curvature (e.g., beverage cans, condiment jars), specular cellophane reflections, "
        "uneven lighting gradients, and microscopic typography. Without specialized optical preprocessing, raw character error "
        "rates escalate dramatically, corrupting critical INS codes and additive strings.\n\n"
        "3. False Deductions and Hallucinatory ML Claims: Several recent academic works attempt to pass uncurated OCR text directly "
        "into black-box supervised machine-learning classifiers or neural networks to predict binary 'healthy' versus 'unhealthy' "
        "ratings. Such architectures lack explainability, frequently fabricate nutritional predictions from misread character noise, "
        "and violate scientific integrity by claiming predictive 'machine learning confidence' for what are fundamentally rule-based "
        "statutory deductions.\n\n"
        "4. Absence of Confidence-Aware Gating and Audit Protocols: When optical recognition degrades or unmapped chemical terms "
        "appear, existing systems silently guess or emit unjustified suitability scores without notifying the user of underlying "
        "optical uncertainty. There is an absence of confidence-aware multimodal architectures capable of evaluating optical clarity, "
        "taxonomy resolution certainty, and barcode decoding validity simultaneously while routing uncertain tokens to human audit."
    )

    # 1.5 Research Motivation and Social Significance
    builder.add_h1("1.5 Research Motivation and Social Significance")
    builder.add_p(
        "The motivation driving this research stems from the critical intersection of modern computer vision, regulatory food "
        "informatics, and consumer healthcare safety. Food labeling laws are enacted precisely to protect human health; however, "
        "the informational protection intended by statutes remains largely theoretical if the practical burden of deciphering "
        "cryptic chemical codes falls entirely upon the cognitive capacity of individual shoppers under time-constrained retail "
        "conditions."
    )
    builder.add_p(
        "By engineering a robust, confidence-aware computational framework, this project seeks to bridge the gap between "
        "complex industrial food chemistry and everyday consumer decision-making. Developing an automated system that operates "
        "efficiently on edge computing and commodity mobile hardware empowers vulnerable demographics—including parents of "
        "hyperactive children, celiac patients, individuals with severe peanut or dairy allergies, diabetic patients monitoring "
        "hidden artificial sweeteners, and ethical vegans—to verify packaging in real time with high scientific certainty."
    )
    builder.add_p(
        "Furthermore, this project is motivated by the academic necessity of establishing rigorous methodological standards in "
        "applied food informatics. By enforcing strict architectural separation between independent analytical modalities, "
        "eliminating deceptive claims regarding predictive machine learning, and implementing a formal Human-in-the-Loop "
        "audit queue for continuous dictionary refinement, this dissertation establishes an authentic, transparent engineering "
        "blueprint for verifiable consumer health applications."
    )

    # 1.6 Project Objectives (Primary & Secondary)
    builder.add_h1("1.6 Project Objectives (Primary & Secondary)")
    builder.add_p(
        "To resolve the identified research gaps and deliver an authentic, high-reliability software system, the investigation "
        "is structured around specific primary and secondary engineering objectives."
    )

    # Table 1.1: Objectives
    headers_t11 = ["Objective ID", "Classification", "Specific Technical Objective Description", "Target Module"]
    data_t11 = [
        ["OBJ-01", "Primary", "Design and implement an automated EAN-13 barcode detection, decoding, and Modulo-10 checksum validation pipeline with external REST database lookup.", "Pipeline A (`barcode.py`)"],
        ["OBJ-02", "Primary", "Engineer an 8-stage adaptive OpenCV image preprocessing pipeline (Configuration B) to overcome packaging curvature, blur, specular reflections, and uneven illumination.", "Pipeline B (`image_preprocessor.py`)"],
        ["OBJ-03", "Primary", "Preserve baseline Configuration A intact and implement resilient automatic error fallback from Configuration B to Configuration A on processing anomalies.", "Pipeline B (`ocr_pipeline.py`)"],
        ["OBJ-04", "Primary", "Construct an authoritative local food additive taxonomy comprising 750 verified INS and E-number substances mapped across 7 functional classes with official regulatory citations.", "Taxonomy Engine (`ins_taxonomy.json`)"],
        ["OBJ-05", "Primary", "Implement a deterministic, rule-based dietary preference matching engine that calculates personalized suitability scores (0-100) with explicit mathematical deductions.", "Scoring Engine (`preference_engine.py`)"],
        ["OBJ-06", "Secondary", "Formulate a 4-dimensional multimodal confidence vector evaluating optical clarity, taxonomy resolution, barcode status, and product identity certainty.", "Audit Subsystem (`audit.py`)"],
        ["OBJ-07", "Secondary", "Implement a Human-in-the-Loop (HITL) audit queue enabling authorized reviewers to confirm, correct, or reject unmapped chemical candidate strings.", "HITL Subsystem (`AuditQueueModal.jsx`)"],
        ["OBJ-08", "Secondary", "Design a responsive Minimalist Health-Tech user interface (React 18 SPA) delivering high-contrast, uncluttered consumer dashboards.", "Frontend (`frontend/src/`)"],
        ["OBJ-09", "Secondary", "Achieve 100% verification across a comprehensive automated test suite spanning unit, integration, boundary, and regression assertions (187 test cases).", "Test Suite (`tests/`)"]
    ]
    builder.add_table("Table 1.1: Primary and Secondary Objectives of the Investigation", headers_t11, data_t11,
                      col_widths=[Inches(1.0), Inches(1.1), Inches(3.4), Inches(1.5)])

    # 1.7 Scope and Operational Constraints (Decoupled Pipelines)
    builder.add_h1("1.7 Scope and Operational Constraints (Decoupled Pipelines)")
    builder.add_p(
        "Defining the precise operational scope and explicit system boundaries is essential for ensuring methodological validity "
        "and preventing unrealistic performance claims:\n\n"
        "1. Decoupled Pipeline Execution: The system strictly decouples Pipeline A (Product Identification via Barcode) from "
        "Pipeline B (Personalised Dietary Analysis via OCR). Automatic ingredient-level cross-source comparison between "
        "OCR-extracted text and Open Food Facts database records is deliberately omitted from the operational scope. Physical "
        "label curvature, printing misalignments, and regional formulation variances introduce optical artifacts that cause "
        "spurious mismatch alerts when compared against crowd-sourced text. The barcode identity serves strictly as independent, "
        "complementary context.\n\n"
        "2. Deterministic Mathematical Scoring: The food suitability scoring engine operates strictly on deterministic mathematical "
        "deductions derived from authoritative regulatory statutes (Codex, FSSAI, EFSA). The system does not claim or utilize "
        "black-box machine learning, neural network classifiers, or fabricated Shapley additive explanations (SHAP) for scoring.\n\n"
        "3. Informational Verification Boundary: The software is engineered as a consumer informational assistance tool. It "
        "does not constitute a medical diagnostic device, a clinical food safety certification, or a legal guarantee against "
        "accidental allergen contamination or industrial cross-contact during packaging."
    )

    # 1.8 Proposed Multimodal Engineering Methodology
    builder.add_h1("1.8 Proposed Multimodal Engineering Methodology")
    builder.add_p(
        "To accomplish the project objectives within the defined scope, a multimodal engineering methodology was formulated. "
        "The system bifurcates the analytical process into two independent, concurrent processing streams that converge exclusively "
        "at the presentation and audit layers."
    )
    builder.add_p(
        "When an EAN-13 barcode image is presented, Pipeline A identifies the barcode bounding box, executes zbar decoding, "
        "and performs rigorous mathematical validation via the Modulo-10 checksum algorithm. Upon validation, it queries the "
        "Open Food Facts international database. If network latency exceeds 4.0 seconds or the device operates offline, the "
        "pipeline falls back gracefully to a curated local benchmark catalog.\n\n"
        "Simultaneously, when packaging label imagery is captured, Pipeline B activates the dual-configuration optical engine. "
        "Configuration B executes the 8-stage OpenCV image enhancement pipeline to stabilize contrast and remove blur before "
        "invoking Tesseract OCR. The extracted character stream is normalized to correct visual misreads (such as I→1 within INS "
        "codes), filtered against Codex Alimentarius valid numeric ranges (100–1599), and mapped against the 750-entry INS taxonomy. "
        "The preference engine evaluates detected substances against user dietary profiles, computes deterministic deductions, "
        "and calculates the 4-dimensional confidence vector to govern audit logging."
    )

    # Insert Figure 1.2
    builder.add_figure(
        "Figure 1.2: Decoupled Multimodal Verification Methodology",
        "fig_1_2_decoupled_methodology.png",
        width_inches=4.0
    )

    # 1.9 Organization and Structure of the Report
    builder.add_h1("1.9 Organization and Structure of the Report")
    builder.add_p(
        "The remainder of this dissertation is organized into six technical chapters, followed by academic references and "
        "institutional documentation:\n\n"
        "• Chapter 2 – Literature Survey: Provides an exhaustive survey of prior research in optical character recognition, "
        "computer vision image preprocessing, barcode standards, and nutritional decision support. Delivers a critical comparative "
        "deconstruction of the baseline paper published in IEEE ICCCA 2025 and establishes the identified research gaps.\n\n"
        "• Chapter 3 – System Requirements and Analysis: Details the existing system deficiencies, formulates the proposed system "
        "capabilities, specifies functional and non-functional requirements, presents the feasibility analysis, and defines formal use cases.\n\n"
        "• Chapter 4 – System Design and Architectural Modeling: Expounds the decoupled system architecture, dual-pipeline design, "
        "relational database schema, and comprehensive UML models including Use Case, DFD (Levels 0, 1, 2), ER, Sequence, Activity, "
        "and Deployment diagrams.\n\n"
        "• Chapter 5 – System Implementation: Documents the concrete software engineering implementation across backend micro-services, "
        "OpenCV preprocessing stages, Tesseract configuration, 750-entry INS taxonomy algorithms, rule-based deduction formulas, "
        "HITL audit queue workflows, and React 18 frontend components, supported by authentic user interface screenshots.\n\n"
        "• Chapter 6 – Testing, Verification, and Performance Evaluation: Details the quality assurance framework, boundary condition "
        "testing, barcode verification logs, latency benchmarking, and the complete execution breakdown of all 187 automated passing tests.\n\n"
        "• Chapter 7 – Conclusion and Future Enhancements: Summarizes project achievements, highlights contributions to academic food "
        "informatics, articulates technical limitations, and charts prospective research avenues including multilingual transformers "
        "and on-device edge neural inference.\n\n"
        "• References: Compiles comprehensive IEEE-style academic citations covering peer-reviewed literature and international regulatory statutes.\n\n"
        "• Part C: Encompasses research paper publication details and professional placement documentation placeholders."
    )

    print("Chapter 1 built successfully.")
