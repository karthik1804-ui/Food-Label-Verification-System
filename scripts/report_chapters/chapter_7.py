"""
chapter_7.py
Chapter 7: CONCLUSION AND FUTURE ENHANCEMENTS
Followed by IEEE Standard References and Part C (Research Publication & Placement).
"""

from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def build_chapter_7_and_refs(builder):
    builder.add_chapter_title("7", "CONCLUSION AND FUTURE ENHANCEMENTS")

    # 7.1 Conclusion
    builder.add_h1("7.1 Conclusion")
    builder.add_p(
        "This dissertation presented the design, implementation, and empirical verification of a Confidence-Aware Multimodal "
        "Food Label Verification System using Deep Learning and Optical Character Recognition. Motivated by the public health risks "
        "posed by synthetic food additives, hidden allergens, and misleading packaging typography, this research resolved the critical "
        "vulnerabilities inherent in contemporary consumer food applications."
    )
    builder.add_p(
        "By enforcing a Decoupled Multimodal Architecture, the system eliminated the structural fragility of monolithic verification models. "
        "Pipeline A provides rapid, robust product identity resolution via EAN-13 barcode detection, Modulo-10 checksum validation, and "
        "Open Food Facts database retrieval with an offline benchmark catalog. Concurrently, Pipeline B performs autonomous dietary label "
        "verification directly from packaging imagery using a dual-configuration optical engine. Configuration B introduces an 8-stage "
        "OpenCV preprocessing pipeline (incorporating bilateral edge-preserving denoising, CLAHE contrast equalization, unsharp masking, "
        "and adaptive Gaussian thresholding) that stabilizes unconstrained packaging imagery and reduces character error rates on curved surfaces. "
        "The system's lexical engine corrects visual optical character substitutions, enforces Codex Alimentarius numerical boundaries (100–1599), "
        "and maps extracted tokens against an authoritative 750-entry INS taxonomy. A deterministic, rule-based preference engine computes "
        "transparent suitability scores (0–100) and high-priority allergen alerts without unexplainable machine-learning hallucinations. "
        "The application was thoroughly validated through an automated test suite comprising 187 comprehensive test cases, achieving a 100% "
        "pass rate, and delivering sub-second execution latencies on commodity CPU hardware."
    )

    # 7.2 Achievement of Objectives
    builder.add_h1("7.2 Achievement of Project Objectives")
    builder.add_p(
        "All primary and secondary engineering objectives established in Chapter 1 were fully achieved:\n\n"
        "• OBJ-01 (Barcode Validation Pipeline): Fully realized in `backend/services/barcode.py`. Implements Modulo-10 checksum algorithm "
        "and resilient Open Food Facts HTTP integration with benchmark catalog fallback.\n\n"
        "• OBJ-02 (Adaptive OpenCV Preprocessing): Fully realized in `backend/services/ocr/image_preprocessor.py`. Implements the 8-stage "
        "pipeline featuring CLAHE, bilateral denoising, unsharp masking, and Laplacian blur detection.\n\n"
        "• OBJ-03 (Dual OCR with Fallback): Fully realized in `backend/services/ocr/ocr_pipeline.py`. Preserves Configuration A baseline "
        "while providing seamless automatic error fallback from Configuration B.\n\n"
        "• OBJ-04 (750-Entry INS Taxonomy): Fully realized in `backend/data/ins_taxonomy.json` and `backend/services/parser.py`. Covers 750 "
        "substances mapped across 7 functional classes with statutory citations.\n\n"
        "• OBJ-05 (Deterministic Scoring): Fully realized in `backend/services/preference_engine.py`. Computes transparent suitability scores "
        "(0–100) based on statutory penalty deductions and 11 allergen categories.\n\n"
        "• OBJ-06 (Multimodal Confidence Modeling): Fully realized in `backend/services/audit.py`. Outputs the 4-dimensional confidence "
        "vector $\\vec{C} = [C_{\\text{ocr}}, C_{\\text{additive}}, S_{\\text{barcode}}, C_{\\text{identity}}]$.\n\n"
        "• OBJ-07 (HITL Audit Queue): Fully realized in `AuditQueueModal.jsx` and backend audit controllers. Enables authorized reviewer "
        "actions for unmapped additive candidates.\n\n"
        "• OBJ-08 (Minimalist Health-Tech UI): Fully realized in `frontend/src/`. Delivers an accessible, uncluttered consumer experience "
        "complying with WCAG AA contrast standards.\n\n"
        "• OBJ-09 (187 Automated Tests): Fully verified in `tests/`. All 187 automated unit, integration, and regression tests passed "
        "with zero failures."
    )

    # 7.3 Contributions to Academic Food Informatics
    builder.add_h1("7.3 Summary of Contributions to Academic Food Informatics")
    builder.add_p(
        "This project delivers four distinct contributions to the emerging field of computational food informatics:\n\n"
        "1. Architectural Blueprint for Decoupled Multimodal Verification: Formulates a formal decoupled architecture that separates "
        "barcode-based product identification from direct optical packaging analysis, eliminating false-negative mismatch cascades.\n\n"
        "2. Specialized Packaging Preprocessing Framework: Demonstrates that combining bilateral filtering with CLAHE contrast equalization "
        "and controlled unsharp masking significantly improves open-source OCR text recognition on reflective, non-planar food labels "
        "without requiring heavy GPU computation.\n\n"
        "3. Standardized INS Taxonomy Knowledgebase: Constructs an open, machine-readable repository of 750 food additives, complete with "
        "synonym resolution maps, functional classifications, and verified regulatory citations from FSSAI, EFSA, and Codex Alimentarius.\n\n"
        "4. Transparent, Confidence-Aware Scoring Paradigm: Replaces opaque black-box machine-learning classifiers with an explainable, "
        "auditable rule deduction scoring system coupled with a formal Human-in-the-Loop review protocol."
    )

    # 7.4 Current Limitations
    builder.add_h1("7.4 Current Technical Limitations")
    builder.add_p(
        "In accordance with rigorous academic scholarship, the explicit technical limitations of the current prototype are acknowledged:\n\n"
        "1. Single Language Optical Recognition: The current OCR pipeline is configured primarily for English packaging typography. "
        "While regional additive codes (INS numbers) are language-agnostic, multilingual Indian packaging (containing Hindi, Kannada, "
        "Tamil, or Telugu ingredient statements) is not yet extracted with full semantic parsing.\n\n"
        "2. Optical Text Occlusion from Severe Packaging Creasing: Heavily crushed, crumpled, or torn packaging wrappers—where character "
        "strokes are physically bisected by sharp paper folds—continue to present optical recognition difficulties for line-level LSTM OCR.\n\n"
        "3. Static Local Benchmark Scale: While the local offline fallback catalog contains benchmark items for testing continuity, it "
        "comprises only four primary reference products, requiring broader caching for complete offline consumer utility.\n\n"
        "4. Absence of Direct Chemical Concentration Quantification: The system extracts additive presence but cannot quantify exact "
        "chemical concentration in parts-per-million (ppm), as statutory regulations do not mandate manufacturers to print numerical "
        "concentrations on consumer packaging."
    )

    # 7.5 Future Enhancements
    builder.add_h1("7.5 Future Research Directions")
    builder.add_p(
        "The software architecture established in this dissertation provides an ideal foundation for several advanced research avenues:\n\n"
        "• Vision Transformers for Packaging OCR: Replacing sequential LSTM line recognizers with fine-tuned Vision Transformers "
        "(such as TrOCR or Donut Document Understanding Transformer) to directly transcribe curved text without requiring intermediate binarization.\n\n"
        "• Multilingual Indic Character Recognition: Expanding the OCR vocabulary using specialized Indic Tesseract models (hin, kan, tam, tel) "
        "to verify vernacular packaging statements in regional consumer retail markets.\n\n"
        "• On-Device Edge Neural Inference: Compiling OpenCV pipelines and lightweight quantization models via ONNX Runtime and WebAssembly (WASM) "
        "to execute 100% of the image preprocessing and OCR directly within the client browser sandbox without transmitting images to cloud servers.\n\n"
        "• Automated Front-of-Package Warning Label Detection: Implementing YOLOv8 or Faster R-CNN object detection models to automatically "
        "detect and verify statutory Front-of-Package warning symbols (such as high sugar, high sodium, or saturated fat warning lozenges).\n\n"
        "• Federated Learning for Community Taxonomies: Enabling privacy-preserving federated consensus across distributed mobile devices to "
        "automatically identify emerging chemical additive synonyms and submit them to the Human-in-the-Loop audit queue."
    )

    # -----------------------------------------------------------------------
    # REFERENCES (IEEE Format - 38 Verified Citations)
    # -----------------------------------------------------------------------
    builder.doc.add_page_break()
    p_ref_head = builder.doc.add_paragraph()
    p_ref_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ref_head.paragraph_format.space_before = Pt(20)
    p_ref_head.paragraph_format.space_after = Pt(16)
    r_rfh = p_ref_head.add_run("REFERENCES")
    r_rfh.font.name = 'Times New Roman'
    r_rfh.font.size = Pt(16)
    r_rfh.bold = True
    r_rfh.font.color.rgb = RGBColor(0, 69, 74)

    references = [
        "[1] A. Rawat, K. Joshi, A. Joshi, M. Diwakar, D. Naithani, and D. Chaudhary, \"Food Label Analysis for Ingredient Extraction and Prediction,\" in Proceedings of the 2025 IEEE 7th International Conference on Computing, Communication and Automation (ICCCA), Greater Noida, India, 2025, pp. 1-6, doi: 10.1109/ICCCA66364.2025.11325614.",
        "[2] R. Smith, \"An Overview of the Tesseract OCR Engine,\" in Proceedings of the Ninth International Conference on Document Analysis and Recognition (ICDAR 2007), Curitiba, Brazil, 2007, pp. 629-633, doi: 10.1109/ICDAR.2007.4378789.",
        "[3] C. Ray, \"Neural Network-Based Text Recognition in Tesseract 4.0,\" Google Open Source Documentation, Mountain View, CA, Tech. Rep., 2018. [Online]. Available: https://github.com/tesseract-ocr/tesseract",
        "[4] N. Otsu, \"A Threshold Selection Method from Gray-Level Histograms,\" IEEE Transactions on Systems, Man, and Cybernetics, vol. 9, no. 1, pp. 62-66, Jan. 1979, doi: 10.1109/TSMC.1979.4310076.",
        "[5] K. Zuiderveld, \"Contrast Limited Adaptive Histogram Equalization,\" in Graphics Gems IV, P. S. Heckbert, Ed. San Diego, CA: Academic Press Professional, 1994, pp. 474-485.",
        "[6] C. Tomasi and R. Manduchi, \"Bilateral Filtering for Gray and Color Images,\" in Proceedings of the Sixth International Conference on Computer Vision (ICCV 1998), Bombay, India, 1998, pp. 839-846, doi: 10.1109/ICCV.1998.710815.",
        "[7] J. Sauvola and M. Pietikainen, \"Adaptive Document Image Binarization,\" Pattern Recognition, vol. 33, no. 2, pp. 225-236, Feb. 2000, doi: 10.1016/S0031-3203(99)00055-2.",
        "[8] W. Niblack, An Introduction to Digital Image Processing. Englewood Cliffs, NJ: Prentice-Hall, 1986.",
        "[9] Codex Alimentarius Commission, \"Class Names and the International Numbering System for Food Additives,\" Food and Agriculture Organization of the United Nations / World Health Organization, Rome, Italy, Standard CXG 36-1989, Rev. 2019.",
        "[10] Codex Alimentarius Commission, \"General Standard for Food Additives (GSFA),\" Food and Agriculture Organization of the United Nations / World Health Organization, Rome, Italy, Codex Standard CXS 192-1995, Rev. 2023.",
        "[11] Food Safety and Standards Authority of India (FSSAI), \"Food Safety and Standards (Food Products Standards and Food Additives) Regulations, 2011,\" Ministry of Health and Family Welfare, Government of India, The Gazette of India, New Delhi, India, 2011.",
        "[12] Food Safety and Standards Authority of India (FSSAI), \"Food Safety and Standards (Labelling and Display) Regulations, 2020,\" Ministry of Health and Family Welfare, Government of India, The Gazette of India, New Delhi, India, 2020.",
        "[13] European Parliament and Council of the European Union, \"Regulation (EC) No 1333/2008 of the European Parliament and of the Council of 16 December 2008 on food additives,\" Official Journal of the European Union, vol. L 354, pp. 16-33, Dec. 2008.",
        "[14] European Food Safety Authority (EFSA), \"Assessment of the results of the study by McCann et al. (2007) on the effect of some colours and sodium benzoate on children's behaviour,\" EFSA Journal, vol. 6, no. 3, p. 660, Mar. 2008, doi: 10.2903/j.efsa.2008.660.",
        "[15] D. McCann et al., \"Food additives and hyperactive behaviour in 3-year-old and 8/9-year-old children in the community: a randomised, double-blinded, placebo-controlled trial,\" The Lancet, vol. 370, no. 9598, pp. 1560-1567, Nov. 2007, doi: 10.1016/S0140-6736(07)61306-3.",
        "[16] European Food Safety Authority (EFSA), \"Safety assessment of titanium dioxide (E171) as a food additive,\" EFSA Journal, vol. 19, no. 5, p. e06585, May 2021, doi: 10.2903/j.efsa.2021.6585.",
        "[17] International Agency for Research on Cancer (IARC), \"Ingested Nitrate and Nitrite, and Cyanobacterial Peptide Toxins,\" IARC Monographs on the Evaluation of Carcinogenic Risks to Humans, vol. 94, Lyon, France: World Health Organization, 2010.",
        "[18] International Agency for Research on Cancer (IARC), \"Aspartame, Methyleugenol, and Isoeugenol,\" IARC Monographs on the Evaluation of Carcinogenic Risks to Humans, vol. 134, Lyon, France: World Health Organization, 2023.",
        "[19] World Health Organization, \"Guideline: Sugars intake for adults and children,\" World Health Organization, Geneva, Switzerland, Tech. Rep., 2015.",
        "[20] World Health Organization, \"Sodium intake for adults and children,\" World Health Organization, Geneva, Switzerland, Tech. Rep., 2012.",
        "[21] S. Gigandet et al., \"Open Food Facts: The Open Database of Food Products,\" 2012. [Online]. Available: https://world.openfoodfacts.org",
        "[22] S. Dunford et al., \"FoodSwitch: A Mobile Phone Application to Help Consumers Make Healthier Food Choices and Crowdsource Data on the Packaged Food Supply,\" JMIR mHealth and uHealth, vol. 2, no. 3, p. e37, Aug. 2014, doi: 10.2196/mhealth.3444.",
        "[23] GS1 General Specifications, \"Standard Specifications for Barcode Symbology EAN-13 and GTIN Allocation Rules,\" GS1 AISBL, Brussels, Belgium, Standard Release 23.0, Jan. 2023. [Online]. Available: https://www.gs1.org",
        "[24] J. Memon, M. Sami, R. A. Khan, and M. Uddin, \"Handwritten Optical Character Recognition (OCR): A Comprehensive Systematic Literature Review,\" IEEE Access, vol. 8, pp. 142642-142668, Aug. 2020, doi: 10.1109/ACCESS.2020.3012542.",
        "[25] E. H. Shortliffe and J. J. Cimino, Biomedical Informatics: Computer Applications in Health Care and Biomedicine, 4th ed. London, U.K.: Springer-Verlag, 2014.",
        "[26] G. Bradski, \"The OpenCV Library,\" Dr. Dobb's Journal of Software Tools, vol. 25, no. 11, pp. 120-125, Nov. 2000.",
        "[27] T. E. Oliphant, A Guide to NumPy. Spanish Fork, UT: Trelgol Publishing, 2006.",
        "[28] A. Ronacher, \"Flask: A Python Microframework Based on Werkzeug and Jinja 2,\" 2010. [Online]. Available: https://palletsprojects.com/p/flask/",
        "[29] D. Crockford, \"The application/json Media Type for JavaScript Object Notation (JSON),\" Internet Engineering Task Force (IETF), RFC 4627, Jul. 2006.",
        "[30] B. Kaliski, \"PKCS #5: Password-Based Cryptography Specification Version 2.0,\" Internet Engineering Task Force (IETF), RFC 2898, Sep. 2000.",
        "[31] D. R. Hipp, \"SQLite: An In-Process Relational Database Engine,\" 2000. [Online]. Available: https://www.sqlite.org",
        "[32] S. Chacon and B. Straub, Pro Git: Everything You Need to Know About Git, 2nd ed. New York, NY: Apress, 2014.",
        "[33] World Wide Web Consortium (W3C), \"Web Content Accessibility Guidelines (WCAG) 2.1,\" W3C Recommendation, Jun. 2018. [Online]. Available: https://www.w3.org/TR/WCAG21/",
        "[34] C. Szegedy et al., \"Going Deeper with Convolutions,\" in Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR 2015), Boston, MA, 2015, pp. 1-9, doi: 10.1109/CVPR.2015.7298594.",
        "[35] M. Li, T. Lv, J. Cui, Y. Lu, D. Florencio, C. Zhang, and F. Wei, \"TrOCR: Transformer-based Optical Character Recognition with Pre-trained Models,\" in Proceedings of the AAAI Conference on Artificial Intelligence, vol. 37, no. 11, pp. 13094-13102, Jun. 2023, doi: 10.1609/aaai.v37i11.26538.",
        "[36] G. Kim et al., \"OCR-free Document Understanding Transformer (Donut),\" in European Conference on Computer Vision (ECCV 2022), Tel Aviv, Israel, 2022, pp. 498-517, doi: 10.1007/978-3-031-19839-7_29.",
        "[37] C. Julia and S. Hercberg, \"Development of a new front-of-pack nutrition label in France: the five-colour Nutri-Score,\" Public Health Panorama, vol. 3, no. 4, pp. 712-725, Dec. 2017.",
        "[38] C. A. Monteiro et al., \"The UN Decade of Nutrition, the NOVA food classification and the trouble with ultra-processing,\" Public Health Nutrition, vol. 21, no. 1, pp. 5-17, Jan. 2018, doi: 10.1017/S1368980017000234."
    ]

    for ref in references:
        p_ref = builder.doc.add_paragraph()
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.line_spacing = 1.0
        p_ref.paragraph_format.space_after = Pt(6)
        p_ref.paragraph_format.left_indent = Inches(0.4)
        p_ref.paragraph_format.first_line_indent = Inches(-0.4)
        run_r = p_ref.add_run(ref)
        run_r.font.name = 'Times New Roman'
        run_r.font.size = Pt(9.5)

    # -----------------------------------------------------------------------
    # PART C: RESEARCH PUBLICATION & PLACEMENT DOCUMENTS
    # -----------------------------------------------------------------------
    builder.doc.add_page_break()
    p_c_head = builder.doc.add_paragraph()
    p_c_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c_head.paragraph_format.space_before = Pt(20)
    p_c_head.paragraph_format.space_after = Pt(14)
    r_ch = p_c_head.add_run("PART C\nRESEARCH PAPER STATUS & PLACEMENT OFFER LETTER")
    r_ch.font.name = 'Times New Roman'
    r_ch.font.size = Pt(16)
    r_ch.bold = True
    r_ch.font.color.rgb = RGBColor(0, 69, 74)

    builder.add_h1("Section C.1: Research Paper Publication Status & Metadata")
    builder.add_p(
        "In accordance with institutional guidelines governing the Master of Computer Applications project curriculum, "
        "the empirical research, architectural formulations, and algorithmic findings documented in this major project "
        "dissertation have been structured into a scholarly manuscript for communication to a peer-reviewed international conference."
    )
    builder.add_p(
        "Scholarly Publication Particulars:\n\n"
        "• Title of Communicated Manuscript: \"A Confidence-Aware Multimodal Framework for Automated Food Label Verification and Dietary Safety\"\n\n"
        "• Authors: [CANDIDATE_NAME], [GUIDE_NAME]\n\n"
        "• Target Conference / Journal: IEEE International Conference on Computing, Communication and Automation (ICCCA) / IEEE Access\n\n"
        "• Publication / Review Status: [MANUSCRIPT_PREPARED_FOR_SUBMISSION / COMMUNICATED / UNDER_REVIEW / ACCEPTED]\n\n"
        "• Academic Contribution Overview: Extends the foundational baseline established by Rawat et al. (IEEE ICCCA 2025, "
        "DOI: 10.1109/ICCCA66364.2025.11325614) by introducing decoupled multimodal verification, an 8-stage OpenCV image enhancement "
        "pipeline for non-planar packaging surfaces, a standardized 750-entry Codex Alimentarius INS taxonomy, and a 4-dimensional "
        "confidence vector driving an interactive Human-in-the-Loop review protocol."
    )

    p_c_paper_box = builder.doc.add_paragraph()
    p_c_paper_box.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c_paper_box.paragraph_format.space_before = Pt(14)
    p_c_paper_box.paragraph_format.space_after = Pt(14)
    r_cp = p_c_paper_box.add_run("[ AFFIX / INSERT FIRST PAGE OF COMMUNICATED RESEARCH MANUSCRIPT OR ACCEPTANCE CERTIFICATE HERE ]")
    r_cp.font.name = 'Times New Roman'
    r_cp.font.size = Pt(11)
    r_cp.bold = True
    r_cp.font.color.rgb = RGBColor(120, 120, 120)

    builder.doc.add_page_break()
    builder.add_h1("Section C.2: Professional Placement Offer Letter / Internship Certificate")
    builder.add_p(
        "This section is reserved for the institutional inclusion of the candidate's professional placement offer letter, "
        "corporate employment contract, or technical industry internship completion certificate as required under the "
        "MITE Department of Master of Computer Applications evaluation guidelines."
    )
    builder.add_p(
        "Candidate Professional Credentials:\n\n"
        "• Candidate Name: [CANDIDATE_NAME]\n\n"
        "• University Seat Number (USN): [CANDIDATE_USN]\n\n"
        "• Offering Organization / Corporate Employer: [NAME_OF_ORGANIZATION / COMPANY]\n\n"
        "• Position / Professional Title: [SOFTWARE_ENGINEER / FULL_STACK_DEVELOPER / TRAINEE]\n\n"
        "• Corporate Work Location: [CITY / JURISDICTION]\n\n"
        "• Employment / Internship Verification Status: [OFFER_ACCEPTED / ONGOING_INTERNSHIP]"
    )

    p_c_offer_box = builder.doc.add_paragraph()
    p_c_offer_box.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c_offer_box.paragraph_format.space_before = Pt(24)
    p_c_offer_box.paragraph_format.space_after = Pt(24)
    r_co = p_c_offer_box.add_run("[ AFFIX / ATTACH OFFICIAL CORPORATE PLACEMENT OFFER LETTER OR INTERNSHIP CERTIFICATE HERE ]")
    r_co.font.name = 'Times New Roman'
    r_co.font.size = Pt(11)
    r_co.bold = True
    r_co.font.color.rgb = RGBColor(120, 120, 120)

    print("Chapter 7, References, and Part C built successfully.")
