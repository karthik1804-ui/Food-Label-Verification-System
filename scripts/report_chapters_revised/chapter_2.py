"""
chapter_2.py
Chapter 2: LITERATURE SURVEY
Revised for genuine academic originality, IEEE in-text citation linking,
and critical comparative deconstruction of baseline literature.
"""

from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def build_chapter_2(builder):
    builder.add_chapter_title("2", "LITERATURE SURVEY")

    # 2.1 Introduction
    builder.add_h1("2.1 Introduction to Related Academic Research")
    builder.add_p(
        "Automated food label verification operates at the intersection of computer vision, document image analysis, "
        "optical character recognition (OCR), toxicological risk modeling, and consumer healthcare informatics. Over the "
        "past two decades, academic researchers and industrial practitioners have explored diverse computational paradigms "
        "to assist shoppers in deciphering packaged product information. Initial efforts concentrated on optical barcode "
        "scanning to query centralized product registries. As mobile computing evolved, investigations expanded into direct "
        "optical recognition of label text, followed by the deployment of statistical learning models to assess nutritional qualities."
    )
    builder.add_p(
        "To establish a rigorous conceptual framework, this chapter reviews the state of the art across six foundational domains: "
        "optical character recognition on physical packaging; advanced image preprocessing for complex, non-planar surfaces; "
        "automated barcode standards; additive taxonomies and statutory frameworks; personalized nutritional decision support architectures; "
        "and multimodal verification workflows. Furthermore, this chapter delivers a critical comparative analysis of the primary "
        "baseline paper published in the 2025 IEEE 7th International Conference on Computing, Communication and Automation (ICCCA), "
        "titled \"Food Label Analysis for Ingredient Extraction and Prediction\" (Rawat et al., DOI: 10.1109/ICCCA66364.2025.11325614) [1]. "
        "Through this systematic critique, the core theoretical and engineering gaps in existing food verification systems are formally articulated."
    )

    # 2.2 Optical Character Recognition on Packaging: State of the Art
    builder.add_h1("2.2 Optical Character Recognition on Packaging: State of the Art")
    builder.add_p(
        "Optical Character Recognition (OCR) constitutes the primary visual modality for digitizing textual ingredients directly "
        "from packaging containers. The architectural evolution of OCR spans three distinct paradigms: early matrix correlation and "
        "template matching (First Generation); structural feature extraction coupled with shallow classifiers such as Support Vector "
        "Machines (Second Generation); and deep recurrent convolutional neural architectures (Third Generation)."
    )
    builder.add_p(
        "Within the open-source software ecosystem, Tesseract—originally developed by Hewlett-Packard Laboratories (1985–1994) and "
        "subsequently maintained by Google—remains the standard academic and industrial reference engine [2]. In its Fourth and Fifth "
        "Generation iterations, Tesseract replaced its legacy line-finding algorithms with an end-to-end neural engine utilizing Long "
        "Short-Term Memory (LSTM) recurrent networks coupled with Connectionist Temporal Classification (CTC) loss [3]. This architecture "
        "generates line-level character sequence hypotheses directly from image slices without requiring discrete character segmentation, "
        "achieving high accuracy on clean, horizontal printed prose."
    )
    builder.add_p(
        "However, foundational studies by Smith [2], Ray [3], and Memon et al. [24] demonstrate that while Tesseract delivers "
        "Character Error Rates (CER) below 1.5% on scanned flat documents, its recognition performance deteriorates significantly "
        "when applied to unconstrained packaging imagery. Food packaging diverges fundamentally from documentary typography: "
        "ingredient statements are routinely set in dense 4.5 pt type to conserve label area; lines wrap across cylindrical cans and "
        "bottles; and flexible cellophane substrates generate intense specular glare under directional store lighting. Without "
        "domain-specific optical preprocessing, baseline Tesseract frequently corrupts numerical digits within INS codes (e.g., misreading "
        "'INS 102' as 'INS I02' or '1N5 102') or merges comma-separated chemical terms into unparsed character clusters."
    )

    # Insert Figure 2.1
    builder.add_figure(
        "Figure 2.1: Taxonomy of Optical Character Recognition Approaches for Food Packaging",
        "fig_2_1_ocr_taxonomy.png",
        width_inches=4.8
    )

    # 2.3 Machine Learning and Image Preprocessing for Complex Scenes
    builder.add_h1("2.3 Machine Learning and Image Preprocessing for Complex Scenes")
    builder.add_p(
        "To mitigate the environmental distortions present in consumer packaging imagery, computer vision preprocessing pipelines "
        "are essential. Document image analysis literature establishes that text recognition accuracy is fundamentally governed by "
        "the local contrast gradient between character stroke boundaries and background substrates."
    )
    builder.add_p(
        "Early approaches relied primarily on global binarization, most notably Otsu's thresholding algorithm [4], which calculates "
        "a single global threshold by maximizing inter-class variance between foreground and background pixels. While computationally "
        "rapid, global binarization collapses under non-uniform illumination—such as store spotlighting, shadow gradients, or curvature "
        "falloff—causing text in darker regions to merge into solid black blocks while bleaching out characters in highlighted regions."
    )
    builder.add_p(
        "To accommodate lighting gradients, local adaptive thresholding algorithms—including Niblack's moving variance method [8] "
        "and Sauvola's formulation [7]—calculate dynamic thresholds for each pixel based on local window statistics. While highly "
        "effective on aged historical documents, applying adaptive binarization to modern packaging frequently amplifies background "
        "graphics, transforming subtle product illustrations, foil reflections, or condensation into spurious character fragments."
    )
    builder.add_p(
        "Consequently, modern computer vision literature emphasizes non-linear contrast enhancement and edge-preserving filtering "
        "prior to thresholding. Zuiderveld [5] introduced Contrast-Limited Adaptive Histogram Equalization (CLAHE), which partitions "
        "the image into contextual tiles, redistributes local contrast, and enforces a strict clip limit to prevent over-amplification "
        "of high-frequency noise. Tomasi and Manduchi [6] formulated the bilateral filter, which combines spatial domain closeness "
        "with radiometric range similarity, smoothing surface noise while preserving sharp character edge boundaries. Coupling bilateral "
        "denoising with CLAHE represents a robust preprocessing approach for non-planar packaging surfaces."
    )

    # Table 2.1: Prior Research Summary
    headers_t21 = ["Author & Year", "Methodology / OCR Architecture", "Domain & Target Scope", "Primary Limitations / Failure Modes"]
    data_t21 = [
        ["Smith (2007) [2]", "Tesseract OCR Engine Overview (Line Finding, Word Slicing, Neural Net)", "General document digitization and flat-bed scanned pages", "Severe degradation on non-planar surfaces; lacks packaging preprocessing."],
        ["Ray (2018) [3]", "Tesseract 4.0 LSTM CTC Neural Architecture Evaluation", "Multi-font printed prose and multilingual document corpora", "Struggles with tiny kerning (<6pt) on complex glossy packaging."],
        ["Memon et al. (2020) [24]", "Hybrid OCR with Adaptive Thresholding for Text Extraction", "Product packaging and label text recognition", "High false positive rate on textured, colorful commercial backgrounds."],
        ["Zuiderveld (1994) [5]", "Contrast-Limited Adaptive Histogram Equalization (CLAHE)", "Biomedical and optical contrast enhancement", "Requires careful clip-limit tuning to avoid amplifying cellophane noise."],
        ["Tomasi & Manduchi (1998) [6]", "Bilateral Filtering for Gray and Color Images", "Edge-preserving image smoothing and noise suppression", "Higher computational complexity than Gaussian smoothing; requires optimization."],
        ["Dunford et al. (2014) [22]", "Smartphone Crowdsourced Food Composition Scanners", "Consumer nutritional mobile assistance (FoodSwitch)", "Relies exclusively on barcodes; fails on packaging ingredient reformulations."],
        ["Codex Alimentarius (2019) [9]", "Class Names and the International Numbering System (CXG 36-1989)", "Global standardized statutory food additive naming", "Provides no software implementation; abstract numbers confuse consumers."],
        ["Rawat et al. (2025) [1]", "Tesseract/EasyOCR + Supervised Classifier (IEEE ICCCA 2025)", "Packaged food ingredient extraction & binary health prediction", "Monolithic OCR failure; unexplainable black-box ML; lacks barcode verification."]
    ]
    builder.add_table("Table 2.1: Summary of Prior Research in OCR-Based Food Ingredient Extraction", headers_t21, data_t21,
                      col_widths=[Inches(1.2), Inches(1.8), Inches(1.8), Inches(2.2)])

    # 2.4 Automated Product Identification Standards (GS1 EAN-13, OFF)
    builder.add_h1("2.4 Automated Product Identification Standards (GS1 EAN-13, OFF)")
    builder.add_p(
        "Parallel to optical text recognition, automated retail identification has developed around standardized machine-readable "
        "barcodes governed internationally by GS1 [23]. The European Article Number (EAN-13) constitutes the standard retail identifier "
        "across Europe, Asia, Latin America, and Africa. An EAN-13 barcode encodes exactly 13 decimal digits structured into a GS1 Prefix "
        "(identifying the issuing national organization, such as 890 for GS1 India), a Manufacturer Code, an Item Reference Code, "
        "and a mandatory Check Digit computed via the Modulo-10 checksum algorithm [23]."
    )
    builder.add_p(
        "In food informatics, the Open Food Facts (OFF) project, founded in 2012 by Stéphane Gigandet [21], represents the primary "
        "collaborative, open-access international repository of food product metadata. Open Food Facts exposes an open REST API "
        "returning structured JSON payloads that include brand names, ingredients, Nutri-Score grades [37], and NOVA food processing "
        "classifications [38]. Prominent consumer applications—such as Yuka and FoodSwitch (Dunford et al. [22])—rely on querying "
        "this database via barcode scans."
    )
    builder.add_p(
        "However, reliance on crowd-sourced barcode registries exposes significant limitations: coverage in regional retail markets is "
        "often incomplete, user-uploaded data may contain transcription errors, and manufacturers frequently alter ingredient formulations "
        "(such as substituting oils or altering preservatives) without updating the assigned GTIN barcode. Under such conditions, "
        "barcode-only applications display obsolete historical records, exposing sensitized consumers to health hazards. This highlights "
        "the necessity of analyzing the physical packaging label directly."
    )

    # 2.5 International Additive Categorization Systems (INS, Codex, FSSAI)
    builder.add_h1("2.5 International Additive Categorization Systems (INS, Codex, FSSAI)")
    builder.add_p(
        "Automated food label verification requires a structured, comprehensive additive reference taxonomy. The global standard is "
        "Codex Alimentarius CXG 36-1989 ('Class Names and the International Numbering System for Food Additives') [9], supported by the "
        "General Standard for Food Additives (CXS 192-1995) [10]. The INS system codifies over 700 distinct chemical substances, "
        "grouping them into functional technological categories based on their primary food manufacturing role."
    )
    builder.add_p(
        "In India, FSSAI regulations [11] establish maximum permitted limits and labeling formats. In the European Union, the European "
        "Food Safety Authority (EFSA) periodically reviews approved additives, adjusting Acceptable Daily Intake (ADI) thresholds or "
        "revoking authorizations when toxicological risks emerge—as exemplified by the 2021 ban on Titanium Dioxide (INS 171 / E171) [16] "
        "due to concerns regarding genotoxicity."
    )
    builder.add_p(
        "Despite available statutory compilations, contemporary consumer software frequently implements narrow, ad-hoc wordlists "
        "covering fewer than 50 common additives. Such limited vocabularies fail to resolve chemical synonyms, technical nomenclature "
        "(e.g., Curcumin vs. Turmeric Yellow vs. C.I. 75300), and sub-classified numerical variants (e.g., INS 500(i), 500(ii)). "
        "This vocabulary restriction results in high false-negative rates during additive identification."
    )

    # 2.6 Personalised Decision Support Systems in Nutrition
    builder.add_h1("2.6 Personalised Decision Support Systems in Nutrition")
    builder.add_p(
        "Personalized nutritional decision support systems recognize that dietary safety is an individualized evaluation reflecting a "
        "user's specific physiological requirements, medical allergies, and ethical lifestyle commitments. Mobile decision support "
        "has progressed from generic nutritional tables into interactive applications that filter ingredients against personal profiles."
    )
    builder.add_p(
        "Clinical decision support literature emphasizes two essential principles: algorithmic transparency and zero-compromise allergen "
        "alerting. As articulated by Shortliffe and Cimino [25], health-assistive systems must provide explicit, auditable explanations "
        "for their recommendations to maintain user trust. When a system flags an ingredient, it must identify the exact offending "
        "substance, state the clinical or preference rationale, and cite the governing regulatory statute. Systems that emit opaque scores "
        "or hide deduction logic behind black-box neural networks violate explainability standards and compromise consumer safety."
    )

    # 2.7 Critical Analysis of Baseline Paper: IEEE ICCCA 2025
    builder.add_h1("2.7 Critical Analysis of Baseline Paper: IEEE ICCCA 2025")
    builder.add_p(
        "The primary direct baseline for this investigation is the research paper authored by Aman Rawat, Ketan Joshi, Aditya Joshi, "
        "Manoj Diwakar, Dhawal Naithani, and Devesh Chaudhary, titled \"Food Label Analysis for Ingredient Extraction and Prediction\", "
        "published in the Proceedings of the 2025 IEEE 7th International Conference on Computing, Communication and Automation (ICCCA) "
        "(DOI: 10.1109/ICCCA66364.2025.11325614) [1]."
    )
    builder.add_p(
        "In the ICCCA 2025 investigation [1], the authors addressed consumer label comprehension by combining optical character "
        "recognition with natural language processing and supervised machine learning classifiers to predict whether a food product "
        "is healthy or unhealthy. Their workflow captures a product label image, executes text extraction using standard Tesseract OCR "
        "or EasyOCR, performs basic string tokenization, and feeds feature vectors into supervised machine learning models (Random "
        "Forest and Support Vector Machines) to output a binary health classification."
    )
    builder.add_p(
        "While Rawat et al. [1] represents a commendable application of computational methods to food labeling, an in-depth "
        "architectural critique reveals critical engineering and methodological vulnerabilities:\n\n"
        "1. Vulnerability of Unaugmented OCR on Curved Packaging: The baseline paper relies on standard OCR engines without domain-specific "
        "optical preprocessing. Their evaluations were conducted primarily on flat, high-contrast label scans. When evaluated against "
        "real-world consumer containers characterized by cylindrical curvature, metallic cellophane glare, and microscopic kerning, "
        "their OCR extraction exhibits substantial character error rates, leading to truncated or corrupted ingredient names.\n\n"
        "2. Absence of Standardized Additive Codification: The baseline architecture treats extracted words as arbitrary NLP tokens, "
        "lacking an underlying standardized taxonomy like the International Numbering System [9]. Consequently, their system cannot "
        "resolve numerical codes to chemical substances (e.g., treating 'INS 211' as an unclassified alphanumeric string rather than "
        "identifying Sodium Benzoate, a preservative of clinical significance [15]).\n\n"
        "3. Unexplainable Black-Box Machine Learning Classification: Training supervised classifiers to output a binary 'healthy' "
        "versus 'unhealthy' rating introduces severe safety risks. In food verification, dietary suitability is personalized and "
        "multi-faceted: a whole-grain cereal containing peanut traces cannot be reduced to a generalized 'healthy' label for an "
        "allergic individual. Furthermore, supervised ML models in this domain are prone to distribution bias and hallucinated inferences "
        "derived from training data artifacts.\n\n"
        "4. Absence of Barcode-Based Identity Decoupling: The ICCCA 2025 architecture completely omits optical barcodes, ignoring the "
        "standard EAN-13 identifier [23] that establishes product identity across international supply chains.\n\n"
        "5. Complete Absence of Confidence Modeling: The baseline system treats all OCR outputs as uniformly valid, emitting definitive "
        "health ratings even when optical recognition confidence is severely compromised. It provides no confidence metrics or "
        "human audit fallback protocols."
    )

    # Insert Figure 2.2
    builder.add_figure(
        "Figure 2.2: Architectural Comparison: IEEE ICCCA 2025 Baseline vs. Proposed System",
        "fig_2_2_baseline_comparison.png",
        width_inches=4.8
    )

    # 2.8 Comparative Analysis Matrix of Contemporary Solutions
    builder.add_h1("2.8 Comparative Analysis Matrix of Contemporary Solutions")
    builder.add_p(
        "To establish the current state of the art, contemporary solutions were evaluated across nine essential engineering and "
        "functional criteria. Table 2.2 presents a qualitative feature comparison among popular commercial applications (Yuka, "
        "FoodSwitch [22], Open Food Facts Mobile [21]), standard OCR baselines [2], the IEEE ICCCA 2025 research study [1], and the "
        "proposed Food Label Verification System."
    )

    # Table 2.2: Feature Matrix
    headers_t22 = ["Capability / Architecture Feature", "Yuka / FoodSwitch", "Open Food Facts Mobile", "Baseline Tesseract OCR", "Rawat et al. (IEEE 2025)", "Proposed Multimodal System"]
    data_t22 = [
        ["Product Identity Modality", "EAN-13 Barcode Only", "EAN-13 Barcode Only", "None (Image Only)", "None (Image Only)", "Decoupled EAN-13 Barcode"],
        ["Direct Label Text Extraction", "No (Database Only)", "Partial (Uncurated)", "Raw Tesseract Engine", "Tesseract / EasyOCR", "Dual-Config Optical Engine"],
        ["Curved Packaging Preprocessing", "Not Applicable", "Not Applicable", "None (Raw Pixels)", "None (Raw Pixels)", "8-Stage Adaptive OpenCV (Config B)"],
        ["Additive Taxonomy Coverage", "Proprietary (~100 items)", "Crowdsourced Open Wiki", "None (Raw Text)", "Unstructured NLP Tokens", "750-Entry Verified Codex INS Taxonomy"],
        ["Personalised Dietary Presets", "Fixed Nutritional Algorithm", "Basic Allergen Flagging", "None", "Binary Global Classifier", "4 Lifestyle Presets + 11 Allergens"],
        ["Scoring Explainability", "Opaque Proprietary Score", "Nutri-Score / NOVA", "None", "Black-Box Supervised ML", "Deterministic Statutory Point Deductions"],
        ["Confidence Gating Architecture", "None", "None", "Single OCR Confidence", "None (Silent Prediction)", "4-Dimensional Confidence Vector"],
        ["Human-in-the-Loop Audit Queue", "None", "Crowdsourced Edits", "None", "None", "Administrative HITL Triage Queue"],
        ["Offline Resilient Architecture", "No (Network Dependent)", "Partial Local Cache", "Fully Local", "No (Server Dependent)", "Offline Benchmark Catalog Fallback"]
    ]
    builder.add_table("Table 2.2: Feature Matrix: Contemporary Food Label Solutions vs. Proposed System", headers_t22, data_t22,
                      col_widths=[Inches(1.8), Inches(1.0), Inches(1.0), Inches(1.0), Inches(1.1), Inches(1.3)])

    # 2.9 Identification of Research Gaps
    builder.add_h1("2.9 Identification of Research Gaps")
    builder.add_p(
        "The literature survey identifies three primary research and engineering gaps in automated food verification:\n\n"
        "• Gap 1 – Packaging Degradation Collapse: Existing systems fail on non-planar, curved, and reflective packaging surfaces "
        "due to reliance on monolithic OCR without specialized adaptive contrast and edge-preserving preprocessing.\n\n"
        "• Gap 2 – Uncurated Vocabulary and Black-Box Estimation: Prior systems either deploy truncated additive dictionaries or "
        "pass uncurated OCR text into black-box ML classifiers, producing unexplainable ratings and risking severe false negatives.\n\n"
        "• Gap 3 – Monolithic Verification Fragility: Coupling barcode identity directly to packaging text generates spurious mismatch "
        "alerts when packaging geometries distort character recognition, while omitting confidence gating leaves users unaware of optical errors."
    )

    # Table 2.3: Research Gaps
    headers_t23 = ["Gap ID", "Academic Domain", "Identified Research / Engineering Vulnerability", "Proposed Technical Countermeasure"]
    data_t23 = [
        ["GAP-01", "Computer Vision Preprocessing", "Monolithic OCR collapses on curved, reflective, non-planar packaging surfaces.", "Adaptive 8-stage OpenCV preprocessing (CLAHE + Bilateral Filtering) in Configuration B."],
        ["GAP-02", "Food Informatics Taxonomy", "Truncated additive wordlists fail to identify INS numerical codes and chemical synonyms.", "Standardized 750-entry INS taxonomy mapped across 7 functional classes with regulatory citations."],
        ["GAP-03", "Risk Scoring Methodology", "Black-box ML models output unexplainable ratings and hallucinate on noisy character data.", "Deterministic mathematical scoring engine with statutory penalty deductions."],
        ["GAP-04", "System Architecture & Auditing", "Absence of optical confidence modeling and mechanism to review unmapped chemical strings.", "4-dimensional multimodal confidence vector governing an interactive HITL audit queue."]
    ]
    builder.add_table("Table 2.3: Summary of Identified Academic Research and Engineering Gaps", headers_t23, data_t23,
                      col_widths=[Inches(0.8), Inches(1.5), Inches(2.5), Inches(2.4)])

    # 2.10 Proposed Technical Solutions & Methodological Innovations
    builder.add_h1("2.10 Proposed Technical Solutions & Methodological Innovations")
    builder.add_p(
        "To resolve the identified gaps, the proposed system introduces four methodological innovations:\n\n"
        "1. Decoupled Dual-Pipeline Architecture: Strictly separates product identity resolution (Pipeline A) from ingredient analysis "
        "(Pipeline B), preventing optical curvature artifacts from triggering false cross-source mismatch alerts.\n\n"
        "2. Adaptive Dual-Configuration Optical Engine: Pairs unaugmented baseline Configuration A with enhanced Configuration B, "
        "integrating bilateral filtering [6], CLAHE [5], and adaptive thresholding [4], [7] with automatic fallback on processing anomalies.\n\n"
        "3. Deterministic Regulatory Risk Engine: Evaluates extracted ingredients against a verified 750-entry INS taxonomy [9] and "
        "11 allergen categories using explicit statutory deduction weights ($w_{\\text{allergen}}=50$, $w_{\\text{lifestyle}}=30$, $w_{\\text{flag}}=15$).\n\n"
        "4. Multimodal Confidence Vector and HITL Triage: Formulates an optical, taxonomic, and product confidence vector that gates "
        "consumer results and routes ambiguous tokens to human administrative review."
    )

    print("Chapter 2 built successfully.")
