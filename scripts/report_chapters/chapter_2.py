"""
chapter_2.py
Chapter 2: LITERATURE SURVEY
Exhaustive literature survey, comparative matrix, critical deconstruction
of baseline paper (IEEE ICCCA 2025), and research gap identification.
"""

from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def build_chapter_2(builder):
    builder.add_chapter_title("2", "LITERATURE SURVEY")

    # 2.1 Introduction
    builder.add_h1("2.1 Introduction to Related Academic Research")
    builder.add_p(
        "Automated food label verification resides at the multidisciplinary nexus of computer vision, document image analysis, "
        "optical character recognition (OCR), natural language processing (NLP), toxicological risk modeling, and consumer healthcare "
        "informatics. Over the past two decades, academic researchers and commercial software developers have explored diverse "
        "computational paradigms to decipher food packaging and assist consumers in making informed dietary selections. Early "
        "investigations concentrated primarily on optical barcode scanning to retrieve centralized static product metadata. As mobile "
        "computing capabilities advanced, research broadened into optical character recognition applied directly to text labels, followed "
        "by the application of statistical machine learning to assess overall nutritional wholesomeness."
    )
    builder.add_p(
        "To establish a rigorous conceptual foundation for the proposed system, this chapter critically reviews the state of the "
        "art across six foundational research domains: optical character recognition applied to packaging text; advanced image "
        "preprocessing techniques for non-planar, unconstrained scenes; automated barcode product identification standards; international "
        "additive taxonomies and regulatory frameworks; personalised nutritional decision support architectures; and multimodal verification "
        "systems. Furthermore, this chapter delivers an exhaustive comparative critique of the recent baseline investigation published "
        "in the proceedings of the IEEE 7th International Conference on Computing, Communication and Automation (ICCCA 2025), titled "
        "\"Food Label Analysis for Ingredient Extraction and Prediction\" (Rawat et al., DOI: 10.1109/ICCCA66364.2025.11325614). "
        "Through this systematic analysis, the fundamental theoretical and practical research gaps governing contemporary food verification "
        "systems are formally identified."
    )

    # 2.2 Optical Character Recognition on Packaging: State of the Art
    builder.add_h1("2.2 Optical Character Recognition on Packaging: State of the Art")
    builder.add_p(
        "Optical Character Recognition (OCR) constitutes the core sensory modality required to extract textual ingredient strings "
        "directly from physical food packages. The evolution of OCR technology spans three distinct historical epochs: traditional "
        "template matching and matrix correlation (First Generation); feature extraction coupled with shallow statistical classifiers "
        "such as Support Vector Machines (Second Generation); and deep recurrent convolutional architectures (Third Generation)."
    )
    builder.add_p(
        "In the domain of open-source OCR architectures, Tesseract—originally developed by Hewlett-Packard Laboratories (1985–1994) "
        "and subsequently open-sourced and maintained by Google—remains the international benchmark. In its Fourth and Fifth Generation "
        "iterations, Tesseract discarded its legacy template-matching pipeline in favor of a neural network engine based on Long "
        "Short-Term Memory (LSTM) recurrent networks coupled with Connectionist Temporal Classification (CTC) loss. This modern "
        "engine constructs line-level character sequence hypotheses without requiring explicit character segmentation, dramatically "
        "improving recognition accuracy on continuous printed prose."
    )
    builder.add_p(
        "However, extensive research by Smith (2007), Ray (2018), and Memon et al. (2020) demonstrates that while Tesseract achieves "
        "character error rates (CER) below 1.5% on clean, scanned documentary pages (such as academic papers or legal briefs), its "
        "accuracy degrades catastrophically when applied to unconstrained consumer packaging imagery. Food packaging labels diverge "
        "radically from standard document typography: they feature non-uniform font scales where ingredient lists are compressed into "
        "dense 4.5 pt type to conserve label surface; non-horizontal baselines wrapping around cylindrical bottle and can surfaces; "
        "and high-gloss metallic foils that create blinding specular reflections under ambient retail lighting. Without specialized "
        "domain-specific optical preprocessing, baseline Tesseract frequently misidentifies critical characters, substituting numerical "
        "digits within INS codes (e.g., mistaking 'INS 102' for 'INS I02' or '1N5 102') or failing to segment comma-delimited additive lists."
    )

    # Insert Figure 2.1
    builder.add_figure(
        "Figure 2.1: Taxonomy of Optical Character Recognition Approaches for Food Packaging",
        "fig_2_1_ocr_taxonomy.png",
        width_inches=4.0
    )

    # 2.3 Machine Learning and Image Preprocessing for Complex Scenes
    builder.add_h1("2.3 Machine Learning and Image Preprocessing for Complex Scenes")
    builder.add_p(
        "To mitigate the environmental distortions inherent in packaged food imagery, researchers have investigated various computer "
        "vision preprocessing pipelines. The foundational literature establishes that the quality of text recognition is inextricably "
        "governed by the signal-to-noise ratio of character stroke edges relative to packaging backgrounds."
    )
    builder.add_p(
        "Early approaches relied primarily on global binarization algorithms, most notably Otsu's thresholding (Otsu, 1979), which "
        "computes an optimal global threshold by maximizing inter-class pixel variance between foreground text and background substrate. "
        "While computationally efficient, global thresholding collapses catastrophically when packaging exhibits non-uniform illumination—such "
        "as directional store lighting, consumer hand shadows, or cylindrical packaging falloff. Under uneven lighting, global thresholds "
        "cause over-segmentation in shadowy quadrants (eroding text into black blobs) and under-segmentation in illuminated regions "
        "(washing out character strokes entirely)."
    )
    builder.add_p(
        "To address non-uniform illumination, adaptive thresholding algorithms—including Niblack's local variance method (Niblack, 1986) "
        "and Sauvola's thresholding (Sauvola & Pietikainen, 2000)—calculate dynamic thresholds for every pixel based on local neighborhood "
        "mean and standard deviation. While superior on degraded historical documents, adaptive binarization on food packaging frequently "
        "amplifies high-frequency background textures, transforming subtle package graphics, woodgrain patterns, or moisture droplets "
        "into spurious foreground noise."
    )
    builder.add_p(
        "Consequently, contemporary computer vision research emphasizes non-linear contrast enhancement and edge-preserving filtering "
        "prior to binarization. Zuiderveld (1994) introduced Contrast-Limited Adaptive Histogram Equalization (CLAHE), which divides the "
        "image into small contextual tiles (typically 8x8 pixels), computes local histograms, and redistributes contrast while imposing "
        "a strict clip limit to prevent over-amplification of noise in flat regions. Tomasi and Manduchi (1998) formulated the bilateral "
        "filter, a non-linear smoothing filter that combines spatial geometric closeness with radiometric photometric similarity, "
        "smoothing packaging surface textures while preserving sharp character boundary gradients. Integrating bilateral denoising with "
        "CLAHE and controlled unsharp masking represents the cutting edge of lightweight, robust edge preprocessing."
    )

    # Table 2.1: Prior Research Summary
    headers_t21 = ["Author & Year", "Methodology / OCR Architecture", "Domain & Target Scope", "Primary Limitations / Failure Modes"]
    data_t21 = [
        ["Smith (2007)", "Tesseract OCR Engine Overview (Line Finding, Word Slicing, Neural Net)", "General document digitization and flat-bed scanned pages", "Severe degradation on non-planar surfaces; lacks packaging preprocessing."],
        ["Ray (2018)", "Tesseract 4.0 LSTM CTC Neural Architecture Evaluation", "Multi-font printed prose and multilingual document corpora", "Struggles with tiny kerning (<6pt) on complex glossy packaging."],
        ["Memon et al. (2020)", "Hybrid OCR with Adaptive Thresholding for Text Extraction", "Product packaging and label text recognition", "High false positive rate on textured, colorful commercial backgrounds."],
        ["Zuiderveld (1994)", "Contrast-Limited Adaptive Histogram Equalization (CLAHE)", "Biomedical and optical contrast enhancement", "Requires careful clip-limit tuning to avoid amplifying cellophane noise."],
        ["Tomasi & Manduchi (1998)", "Bilateral Filtering for Gray and Color Images", "Edge-preserving image smoothing and noise suppression", "Higher computational complexity than Gaussian smoothing; requires optimization."],
        ["Dunford et al. (2014)", "Smartphone Crowdsourced Food Composition Scanners", "Consumer nutritional mobile assistance (FoodSwitch)", "Relies exclusively on barcodes; fails on packaging ingredient reformulations."],
        ["Codex Alimentarius (2019)", "Class Names and the International Numbering System (CXG 36-1989)", "Global standardized statutory food additive naming", "Provides no software implementation; abstract numbers confuse consumers."],
        ["Rawat et al. (2025)", "Tesseract/EasyOCR + Supervised Classifier (IEEE ICCCA 2025)", "Packaged food ingredient extraction & binary health prediction", "Monolithic OCR failure; unexplainable black-box ML; lacks barcode verification."]
    ]
    builder.add_table("Table 2.1: Summary of Prior Research in OCR-Based Food Ingredient Extraction", headers_t21, data_t21,
                      col_widths=[Inches(1.2), Inches(1.8), Inches(1.8), Inches(2.2)])

    # 2.4 Automated Product Identification Standards (GS1 EAN-13, OFF)
    builder.add_h1("2.4 Automated Product Identification Standards (GS1 EAN-13, OFF)")
    builder.add_p(
        "Parallel to direct optical text recognition, automated product identification has evolved around standardized optical machine-readable "
        "barcodes governed internationally by GS1. The European Article Number (EAN-13) barcode constitutes the universal standard for retail "
        "point-of-sale item identification across Europe, Asia, Latin America, and Africa. An EAN-13 barcode encodes exactly 13 decimal digits "
        "structured into four discrete components: a GS1 Prefix (the first 2–3 digits designating the issuing national GS1 organization, "
        "such as 890 for GS1 India); a Manufacturer Code; an Item Reference Code assigned by the brand; and a final Check Digit computed "
        "via a mandatory Modulo-10 checksum algorithm."
    )
    builder.add_p(
        "In the computational food informatics domain, the Open Food Facts (OFF) project, founded in 2012 by Stéphane Gigandet, represents "
        "the largest open, collaborative, crowd-sourced international database of food packaging metadata. Open Food Facts exposes an open "
        "REST API (e.g., `https://world.openfoodfacts.org/api/v0/product/{ean}.json`) that returns extensive JSON payloads encompassing "
        "product names, brands, categories, nutritional tables, Nutri-Score grades, NOVA food processing classifications, and ingredient "
        "strings. Commercial applications—such as Yuka, FoodSwitch (Dunford et al., 2014), and Open Food Facts mobile—rely entirely on "
        "querying this database via barcode scans."
    )
    builder.add_p(
        "However, extensive evaluation of crowd-sourced databases reveals significant limitations: coverage in emerging markets is often "
        "sparse or outdated; user-uploaded ingredient transcriptions contain typographical errors; and crucially, manufacturers frequently "
        "reformulate packaged food compositions—altering oil types, substituting sweeteners, or introducing novel preservatives—without "
        "reissuing a new EAN-13 barcode. In such scenarios, barcode-only systems present outdated historical data, creating severe hazards "
        "for allergic or health-compromised consumers. This underscores the necessity of verifying the physical packaging label directly."
    )

    # 2.5 International Additive Categorization Systems (INS, Codex, FSSAI)
    builder.add_h1("2.5 International Additive Categorization Systems (INS, Codex, FSSAI)")
    builder.add_p(
        "A critical prerequisite for automated food verification is the existence of an authoritative, structured, and comprehensive "
        "additive taxonomy. The international benchmark standard is Codex Alimentarius CXG 36-1989 ('Class Names and the International "
        "Numbering System for Food Additives'), adopted by the Codex Alimentarius Commission and periodically updated. The INS framework "
        "identifies over 700 distinct technological substances, categorizing them into functional classes based on their primary technological "
        "purpose in food manufacturing."
    )
    builder.add_p(
        "Under FSSAI regulations in India, the Food Safety and Standards (Food Products Standards and Food Additives) Regulations, 2011, "
        "prescribe statutory maximum permitted levels (GMP or numerical limits in mg/kg) across specific food categories. Similarly, the "
        "European Food Safety Authority (EFSA) conducts rigorous re-evaluations of all food additives authorized prior to 2009 under "
        "Regulation (EC) No 257/2010. EFSA re-evaluations periodically lower Acceptable Daily Intake (ADI) thresholds or revoke authorization "
        "entirely when new toxicological evidence emerges—as observed in the 2021 ban of Titanium Dioxide (INS 171 / E171) as a food additive "
        "due to concerns regarding genotoxicity and particle accumulation."
    )
    builder.add_p(
        "Despite the availability of these regulatory catalogs, contemporary software systems frequently implement rudimentary, ad-hoc "
        "keyword dictionaries containing fewer than 50 common additives. Such truncated vocabularies fail to capture regional chemical "
        "synonyms, alternative nomenclature (e.g., Curcumin vs. Turmeric Yellow vs. C.I. 75300), and sub-classified numerical derivatives "
        "(e.g., INS 500(i), 500(ii), 500(iii)). This vocabulary truncation leads to substantial false-negative rates in additive identification."
    )

    # 2.6 Personalised Decision Support Systems in Nutrition
    builder.add_h1("2.6 Personalised Decision Support Systems in Nutrition")
    builder.add_p(
        "The paradigm of personalized nutrition recognizes that nutritional suitability is not a universal constant, but a subjective "
        "interaction between specific food components and an individual's unique biological, physiological, and ethical profile. "
        "Decision support systems in nutrition have evolved from generic educational kiosks into intelligent mobile applications capable "
        "of filtering ingredients based on user profiles."
    )
    builder.add_p(
        "Research in clinical decision support emphasizes two paramount principles: algorithmic transparency and zero-compromise "
        "allergen gating. As articulated by Shortliffe and Cimino (2014), medical and health-assistive systems must provide clear, "
        "auditable rationales for their recommendations to maintain clinician and patient trust. When an application advises a user to "
        "avoid a product, it must state the exact conflicting ingredient, the underlying clinical or preference rationale, and the "
        "regulatory source. Systems that emit opaque scores or conceal deduction criteria behind black-box neural networks violate basic "
        "tenets of clinical explainability and disempower the user."
    )

    # 2.7 Critical Analysis of Baseline Paper: IEEE ICCCA 2025
    builder.add_h1("2.7 Critical Analysis of Baseline Paper: IEEE ICCCA 2025")
    builder.add_p(
        "A pivotal baseline investigation in this academic domain is the recent research paper authored by Aman Rawat, Ketan Joshi, "
        "Aditya Joshi, Manoj Diwakar, Dhawal Naithani, and Devesh Chaudhary, titled \"Food Label Analysis for Ingredient Extraction "
        "and Prediction\", published in the Proceedings of the 2025 IEEE 7th International Conference on Computing, Communication and "
        "Automation (ICCCA), bearing DOI: 10.1109/ICCCA66364.2025.11325614."
    )
    builder.add_p(
        "The authors of the ICCCA 2025 paper aimed to address consumer difficulty in deciphering packaged food labels by deploying "
        "optical character recognition combined with natural language processing and machine learning classifiers to predict whether a "
        "food product is healthy or unhealthy. Their architecture captures a product label image, executes text extraction using "
        "standard Tesseract OCR or EasyOCR, applies basic NLP text cleaning, tokenizes ingredient strings, and feeds numerical feature "
        "vectors into supervised machine learning algorithms (such as Random Forest and Support Vector Machines) to output a binary "
        "classification rating."
    )
    builder.add_p(
        "While the ICCCA 2025 paper represents a commendable initiative in applying computational techniques to food labeling, an "
        "in-depth academic and architectural examination reveals critical methodological, algorithmic, and practical vulnerabilities:\n\n"
        "1. Monolithic OCR Vulnerability on Real-World Packaging: The baseline paper relies on standard OCR engines without domain-specific "
        "optical preprocessing. Their experimental evaluations were conducted primarily on high-contrast, flat label scans. When evaluated "
        "against real-world packaged items characterized by curved cylindrical geometry, reflective plastic wrapping, and microscopic "
        "kerning, their OCR extraction exhibits substantial character error rates, leading to truncated or corrupted ingredient names.\n\n"
        "2. Lack of Structured Additive Standardization: The baseline paper treats extracted ingredients as arbitrary NLP text tokens, "
        "lacking an underlying, standardized taxonomy such as the International Numbering System (INS). Consequently, the system fails to "
        "resolve numerical additive codes to their chemical substances (e.g., treating 'INS 211' as an unclassified alphanumeric token "
        "rather than identifying it as Sodium Benzoate, a preservative of significant pediatric concern).\n\n"
        "3. Unexplainable Black-Box Machine Learning Classification: The baseline paper trains a supervised machine-learning classifier "
        "to output a binary 'wholesome' versus 'unwholesome' prediction. In food safety, binary predictions are fundamentally unexplainable "
        "and scientifically hazardous. A packaged item containing a single critical allergen (e.g., peanut traces in an otherwise whole-grain "
        "cereal) cannot be characterized by an aggregated 'healthy' score. Furthermore, supervised ML models in this domain are prone to "
        "spurious correlations and hallucinated inferences based on training set distribution bias.\n\n"
        "4. Absence of Barcode-Based Product Identity Decoupling: The ICCCA 2025 system completely ignores optical barcodes, discarding "
        "the standard EAN-13 identifier that uniquely establishes product identity across international supply chains.\n\n"
        "5. Complete Absence of Confidence Modeling: The baseline system treats all OCR outputs as equally valid, emitting definitive "
        "health ratings even when optical recognition confidence is critically compromised. It provides no confidence metrics or "
        "human audit fallback protocols."
    )

    # Insert Figure 2.2
    builder.add_figure(
        "Figure 2.2: Architectural Comparison: IEEE ICCCA 2025 Baseline vs. Proposed System",
        "fig_2_2_baseline_comparison.png",
        width_inches=4.0
    )

    # 2.8 Comparative Analysis Matrix
    builder.add_h1("2.8 Comparative Analysis Matrix of Contemporary Solutions")
    builder.add_p(
        "To synthesize the literature survey and rigorously establish the state of the art, contemporary solutions were evaluated across "
        "nine essential engineering and domain criteria. Table 2.2 presents a comprehensive feature comparison between popular commercial "
        "consumer applications (Yuka, FoodSwitch, Open Food Facts Mobile), standard OCR baselines, the IEEE ICCCA 2025 research paper, "
        "and the proposed Food Label Verification System."
    )

    # Table 2.2: Feature Matrix
    headers_t22 = ["Capability / Architectural Criterion", "Yuka / Commercial", "Open Food Facts", "Rawat et al. (ICCCA 2025)", "Proposed System"]
    data_t22 = [
        ["Barcode EAN-13 Support & Checksum Validation", "Yes (Barcode only)", "Yes (Barcode only)", "No (OCR only)", "Yes (Pipeline A + Modulo-10)"],
        ["Direct Packaging OCR Extraction", "No", "Limited (Cloud)", "Yes (Monolithic Tesseract)", "Yes (Dual Config A/B Tesseract)"],
        ["Adaptive OpenCV Preprocessing (CLAHE, Blur)", "No", "No", "No", "Yes (8-Stage Config B Pipeline)"],
        ["Structured INS Additive Taxonomy Size", "Proprietary (~300)", "Community (~400)", "None (Ad-hoc tokens)", "750 Curated Additive Entries"],
        ["Decoupled Multimodal Architecture", "No", "No", "No", "Yes (Pipeline A || Pipeline B)"],
        ["Personalised Dietary Presets & Allergens", "Paid / Basic", "Basic Allergens", "No (Universal ML rating)", "Yes (4 Presets + 11 Allergens)"],
        ["Explainable Scoring Methodology", "Nutri-Score / Opaque", "Nutri-Score", "Black-Box ML Classifier", "Deterministic Rule Deductions"],
        ["Multimodal Confidence Vector & Quality Gating", "No", "No", "No", "Yes ([C_ocr, C_add, S_bar, C_id])"],
        ["Human-in-the-Loop (HITL) Audit Queue", "No", "Community Edit", "No", "Yes (Auditor Review Interface)"]
    ]
    builder.add_table("Table 2.2: Feature Matrix: Contemporary Food Label Solutions vs. Proposed System", headers_t22, data_t22,
                      col_widths=[Inches(2.0), Inches(1.2), Inches(1.2), Inches(1.4), Inches(1.4)])

    # Table 2.3: Comparative Analysis against Baseline
    headers_t23 = ["Dimension", "Baseline: Rawat et al. (IEEE ICCCA 2025)", "Proposed: Food Label Verification System"]
    data_t23 = [
        ["Core Pipeline Architecture", "Monolithic: Image -> OCR -> NLP -> Classifier", "Decoupled Multimodal: Pipeline A (Barcode) || Pipeline B (OCR)"],
        ["Image Preprocessing", "None; relies on standard OCR binarization", "8-stage OpenCV (aspect resizing, bilateral, CLAHE, unsharp mask, adaptive thresh)"],
        ["OCR Operational Model", "Single engine pass; vulnerable to collapse", "Dual Configuration (Config A Baseline + Config B Enhanced + Error Fallback)"],
        ["Additive Resolution", "Unstructured NLP word tokens", "Codex-range regex (100-1599) + 750-entry INS taxonomy mapping"],
        ["Scoring & Evaluation", "Supervised ML classifier (binary healthy/unhealthy)", "Deterministic rule-based deduction (0-100) + independent allergen alert gating"],
        ["Barcode & Database", "Omitted completely", "EAN-13 Modulo-10 validation + Open Food Facts API + 4-item offline catalog"],
        ["Audit & Quality Gating", "None; blind prediction emission", "4D confidence vector + SQLite logging + HITL audit review queue"]
    ]
    builder.add_table("Table 2.3: Comparative Analysis against Baseline (Rawat et al., IEEE ICCCA 2025)", headers_t23, data_t23,
                      col_widths=[Inches(1.8), Inches(2.7), Inches(2.7)])

    # 2.9 Identified Research Gaps
    builder.add_h1("2.9 Identified Research Gaps in Contemporary Systems")
    builder.add_p(
        "Based on the thorough examination of prior literature and contemporary implementations, five pivotal research gaps were identified:\n\n"
        "• Gap 1: Inadequate Optical Preprocessing for Non-Planar Packaging. Prior systems treat food packaging as flat documentary paper, "
        "neglecting the severe optical degradations introduced by cylinder curvature, cellophane glare, and microscopic kerning. A robust, "
        "adaptive preprocessing pipeline capable of dynamically handling blur and uneven lighting while preserving character edges is missing.\n\n"
        "• Gap 2: Over-Coupling and False Mismatches in Multimodal Food Scanners. Existing conceptual multimodal systems attempt to cross-match "
        "OCR text directly against crowd-sourced barcode database text. Because physical packaging text differs in punctuation, formatting, and "
        "regional variants, cross-matching generates catastrophic false-negative alarms. A decoupled multimodal architecture is urgently required.\n\n"
        "• Gap 3: Absence of Standardized Regulatory Additive Knowledgebases. Academic models rely on ad-hoc token matching without "
        "grounding in comprehensive international codifications. There is an absence of software systems that bridge raw OCR tokens to the "
        "full 750-substance Codex Alimentarius and FSSAI taxonomy with explicit hazard weights and alternative chemical synonyms.\n\n"
        "• Gap 4: Opacity and Scientific Irresponsibility in Scoring Models. Previous works deploy unexplainable machine learning classifiers "
        "that output subjective 'healthiness' scores without transparent mathematical rationales, violating clinical decision support principles. "
        "There is a need for deterministic, auditable rule-based scoring systems with zero ML hallucination.\n\n"
        "• Gap 5: Complete Deficiency of Confidence-Aware Gating and Audit Protocols. Current applications exhibit zero awareness of their "
        "own recognition uncertainty, silently guessing on corrupt characters. Systems lack multimodal confidence vectors that gate outputs "
        "and automatically route ambiguous chemical strings to human-in-the-loop review."
    )

    # 2.10 Summary
    builder.add_h1("2.10 Summary")
    builder.add_p(
        "This chapter surveyed the foundational literature underpinning automated food label analysis, detailing historical developments "
        "in optical character recognition, computer vision contrast enhancement, GS1 barcode standards, and regulatory additive codification. "
        "A rigorous comparative deconstruction of the IEEE ICCCA 2025 baseline paper (Rawat et al.) highlighted critical vulnerabilities "
        "in monolithic OCR, unexplainable machine learning, and absence of barcode identification. By systematically identifying five "
        "fundamental research gaps, this chapter establishes the academic necessity and technical justification for the proposed "
        "Confidence-Aware Multimodal Food Label Verification System."
    )

    print("Chapter 2 built successfully.")
