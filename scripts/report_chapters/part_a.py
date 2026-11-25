"""
part_a.py
Generates Part A (Preliminary Pages) for MITE MCA Project Report:
- Title Page (Page i - suppressed)
- Institutional Certificate of Approval
- Student Declaration
- Acknowledgements
- Abstract
- Table of Contents
- List of Figures
- List of Tables
- List of Abbreviations
"""

import docx
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

def build_part_a(builder):
    doc = builder.doc
    section1 = doc.sections[0]
    builder.configure_section_margins(section1, is_part_a=True)

    # -----------------------------------------------------------------------
    # 1. TITLE PAGE / COVER PAGE
    # -----------------------------------------------------------------------
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(18)
    p.paragraph_format.line_spacing = 1.2
    run = p.add_run("A CONFIDENCE-AWARE MULTIMODAL FOOD LABEL\nVERIFICATION SYSTEM USING DEEP LEARNING AND OCR")
    run.font.name = 'Times New Roman'
    run.font.size = Pt(16)
    run.bold = True
    run.font.color.rgb = RGBColor(0, 69, 74)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(14)
    p_sub.paragraph_format.space_after = Pt(20)
    p_sub.paragraph_format.line_spacing = 1.3
    run_sub = p_sub.add_run(
        "A Project Report Submitted in Partial Fulfillment of the Requirements\n"
        "for the Award of the Degree of\n\n"
        "MASTER OF COMPUTER APPLICATIONS"
    )
    run_sub.font.name = 'Times New Roman'
    run_sub.font.size = Pt(13)
    run_sub.bold = True

    p_by = doc.add_paragraph()
    p_by.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_by.paragraph_format.space_before = Pt(24)
    p_by.paragraph_format.space_after = Pt(6)
    r_by = p_by.add_run("Submitted by:\n")
    r_by.font.name = 'Times New Roman'
    r_by.font.size = Pt(11)
    r_by.italic = True
    r_name = p_by.add_run("[CANDIDATE_NAME]\n")
    r_name.font.name = 'Times New Roman'
    r_name.font.size = Pt(13)
    r_name.bold = True
    r_usn = p_by.add_run("USN: [CANDIDATE_USN]")
    r_usn.font.name = 'Times New Roman'
    r_usn.font.size = Pt(12)

    p_guide = doc.add_paragraph()
    p_guide.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_guide.paragraph_format.space_before = Pt(20)
    p_guide.paragraph_format.space_after = Pt(24)
    r_gu = p_guide.add_run("Under the Guidance of:\n")
    r_gu.font.name = 'Times New Roman'
    r_gu.font.size = Pt(11)
    r_gu.italic = True
    r_gname = p_guide.add_run("[GUIDE_NAME]\n")
    r_gname.font.name = 'Times New Roman'
    r_gname.font.size = Pt(13)
    r_gname.bold = True
    r_gdes = p_guide.add_run("[GUIDE_DESIGNATION]\nDepartment of Master of Computer Applications")
    r_gdes.font.name = 'Times New Roman'
    r_gdes.font.size = Pt(11)

    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(30)
    p_inst.paragraph_format.space_after = Pt(0)
    p_inst.paragraph_format.line_spacing = 1.3
    r_inst = p_inst.add_run(
        "DEPARTMENT OF MASTER OF COMPUTER APPLICATIONS\n"
        "MANGALORE INSTITUTE OF TECHNOLOGY AND ENGINEERING (MITE)\n"
        "(An Autonomous Institution, Affiliated to VTU, Belagavi)\n"
        "Badaga Mijar, Moodabidri, Mangalore – 574225, Karnataka, India\n\n"
        "ACADEMIC YEAR: 2026–2027"
    )
    r_inst.font.name = 'Times New Roman'
    r_inst.font.size = Pt(11.5)
    r_inst.bold = True
    r_inst.font.color.rgb = RGBColor(0, 69, 74)

    # -----------------------------------------------------------------------
    # 2. INSTITUTIONAL CERTIFICATE
    # -----------------------------------------------------------------------
    doc.add_page_break()
    p_c_head = doc.add_paragraph()
    p_c_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c_head.paragraph_format.space_before = Pt(18)
    p_c_head.paragraph_format.space_after = Pt(4)
    r_ch = p_c_head.add_run(
        "MANGALORE INSTITUTE OF TECHNOLOGY AND ENGINEERING\n"
        "DEPARTMENT OF MASTER OF COMPUTER APPLICATIONS\n"
        "MOODABIDRI – 574225"
    )
    r_ch.font.name = 'Times New Roman'
    r_ch.font.size = Pt(12)
    r_ch.bold = True
    r_ch.font.color.rgb = RGBColor(0, 69, 74)

    p_c_bar = doc.add_paragraph()
    p_c_bar.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c_bar.paragraph_format.space_after = Pt(16)
    p_c_bar.add_run("―" * 42)

    p_cert_title = doc.add_paragraph()
    p_cert_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cert_title.paragraph_format.space_after = Pt(16)
    r_ct = p_cert_title.add_run("CERTIFICATE")
    r_ct.font.name = 'Times New Roman'
    r_ct.font.size = Pt(15)
    r_ct.bold = True
    r_ct.font.color.rgb = RGBColor(0, 69, 74)

    builder.add_p(
        "This is to certify that the project work entitled \"A Confidence-Aware Multimodal Food "
        "Label Verification System Using Deep Learning and OCR\" is a bonafide work carried out by "
        "[CANDIDATE_NAME] bearing USN [CANDIDATE_USN] in partial fulfillment for the award of the degree of "
        "Master of Computer Applications from Mangalore Institute of Technology and Engineering, Moodabidri, "
        "affiliated to Visvesvaraya Technological University, Belagavi, during the academic year 2026–2027.",
        space_after=12
    )
    builder.add_p(
        "It is certified that all corrections and suggestions indicated during internal assessments and reviews "
        "have been incorporated in the report deposited in the departmental library. The project report has been "
        "approved as it satisfies the academic requirements in respect of project work prescribed for the said degree.",
        space_after=36
    )

    # Signatures table
    tbl_sig = doc.add_table(rows=2, cols=3)
    tbl_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    sig_labels = [
        ("_____________________\n[GUIDE_NAME]\nInternal Project Guide", WD_ALIGN_PARAGRAPH.LEFT),
        ("_____________________\n[HOD_NAME]\nHead of the Department", WD_ALIGN_PARAGRAPH.CENTER),
        ("_____________________\n[PRINCIPAL_NAME]\nPrincipal / Head of Institution", WD_ALIGN_PARAGRAPH.RIGHT)
    ]
    for idx, (label, align) in enumerate(sig_labels):
        cell = tbl_sig.rows[0].cells[idx]
        p = cell.paragraphs[0]
        p.alignment = align
        r = p.add_run(label)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)
        r.bold = True

    p_viva = doc.add_paragraph()
    p_viva.paragraph_format.space_before = Pt(36)
    p_viva.paragraph_format.space_after = Pt(12)
    r_v = p_viva.add_run("Viva-Voce Examination:\n\n")
    r_v.font.name = 'Times New Roman'
    r_v.font.size = Pt(11)
    r_v.bold = True
    r_v2 = p_viva.add_run(
        "Name of the Examiners:                                                    Signature with Date:\n\n"
        "1. [EXTERNAL_EXAMINER_1]                                                  _____________________\n\n"
        "2. [EXTERNAL_EXAMINER_2]                                                  _____________________"
    )
    r_v2.font.name = 'Times New Roman'
    r_v2.font.size = Pt(10.5)

    # -----------------------------------------------------------------------
    # 3. DECLARATION
    # -----------------------------------------------------------------------
    doc.add_page_break()
    p_d_head = doc.add_paragraph()
    p_d_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_d_head.paragraph_format.space_before = Pt(18)
    p_d_head.paragraph_format.space_after = Pt(18)
    r_dh = p_d_head.add_run("DECLARATION")
    r_dh.font.name = 'Times New Roman'
    r_dh.font.size = Pt(15)
    r_dh.bold = True
    r_dh.font.color.rgb = RGBColor(0, 69, 74)

    builder.add_p(
        "I, [CANDIDATE_NAME], student of Master of Computer Applications at Mangalore Institute of Technology and "
        "Engineering, Moodabidri, bearing USN [CANDIDATE_USN], hereby declare that the project work entitled "
        "\"A Confidence-Aware Multimodal Food Label Verification System Using Deep Learning and OCR\" has been "
        "independently developed and compiled by me under the guidance of [GUIDE_NAME], [GUIDE_DESIGNATION], "
        "Department of Master of Computer Applications.",
        space_after=12
    )
    builder.add_p(
        "I declare that the matter presented in this report has not been submitted previously, in part or in full, "
        "to any other university or institute for the award of any degree, diploma, fellowship, or other similar title.",
        space_after=12
    )
    builder.add_p(
        "I further affirm that the software algorithms, empirical test cases, database schemas, and analytical data "
        "documented in this dissertation represent original work and that all scholarly publications, international "
        "statutes, and software frameworks utilized have been appropriately acknowledged and cited according to "
        "established academic standards.",
        space_after=40
    )

    p_d_sig = doc.add_paragraph()
    p_d_sig.paragraph_format.line_spacing = 1.3
    r_ds = p_d_sig.add_run(
        "Date: ____________________                                                _____________________\n"
        "Place: Moodabidri                                                         [CANDIDATE_NAME]\n"
        "                                                                          USN: [CANDIDATE_USN]"
    )
    r_ds.font.name = 'Times New Roman'
    r_ds.font.size = Pt(11)
    r_ds.bold = True

    # -----------------------------------------------------------------------
    # 4. ACKNOWLEDGEMENTS
    # -----------------------------------------------------------------------
    doc.add_page_break()
    p_a_head = doc.add_paragraph()
    p_a_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_a_head.paragraph_format.space_before = Pt(18)
    p_a_head.paragraph_format.space_after = Pt(18)
    r_ah = p_a_head.add_run("ACKNOWLEDGEMENT")
    r_ah.font.name = 'Times New Roman'
    r_ah.font.size = Pt(15)
    r_ah.bold = True
    r_ah.font.color.rgb = RGBColor(0, 69, 74)

    builder.add_p(
        "The completion of this major project report marks a significant milestone in my academic journey. "
        "I express my profound gratitude to all the individuals whose guidance, encouragement, and support "
        "made the successful realization of this investigation possible.",
        space_after=10
    )
    builder.add_p(
        "First and foremost, I express my sincere gratitude to our esteemed President and Management of Mangalore "
        "Institute of Technology and Engineering (MITE) for providing state-of-the-art infrastructural facilities "
        "and an academically enriching environment.",
        space_after=10
    )
    builder.add_p(
        "I express my respectful thanks to Dr. [PRINCIPAL_NAME], Principal, MITE, for his continuous encouragement "
        "and scholarly leadership throughout my course of study.",
        space_after=10
    )
    builder.add_p(
        "I extend my heartfelt gratitude to Dr. [HOD_NAME], Head of the Department of Master of Computer Applications, "
        "for his constructive feedback, academic support, and for providing the necessary facilities to execute this "
        "multimodal engineering project.",
        space_after=10
    )
    builder.add_p(
        "I am deeply indebted to my project guide, [GUIDE_NAME], [GUIDE_DESIGNATION], Department of MCA, for their "
        "invaluable guidance, meticulous reviews, and constant technical encouragement throughout the conceptualization, "
        "algorithmic implementation, and dissertation preparation phases of this project.",
        space_after=10
    )
    builder.add_p(
        "I also thank all the teaching and non-teaching faculty members of the Department of MCA for their direct and "
        "indirect assistance. Finally, I thank my parents, family members, and peers for their unceasing patience, "
        "moral encouragement, and understanding throughout the course of this study.",
        space_after=30
    )

    p_a_sig = doc.add_paragraph()
    p_a_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_as = p_a_sig.add_run("[CANDIDATE_NAME]\nUSN: [CANDIDATE_USN]")
    r_as.font.name = 'Times New Roman'
    r_as.font.size = Pt(11)
    r_as.bold = True

    # -----------------------------------------------------------------------
    # 5. ABSTRACT
    # -----------------------------------------------------------------------
    doc.add_page_break()
    p_ab_head = doc.add_paragraph()
    p_ab_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ab_head.paragraph_format.space_before = Pt(18)
    p_ab_head.paragraph_format.space_after = Pt(18)
    r_abh = p_ab_head.add_run("ABSTRACT")
    r_abh.font.name = 'Times New Roman'
    r_abh.font.size = Pt(15)
    r_abh.bold = True
    r_abh.font.color.rgb = RGBColor(0, 69, 74)

    builder.add_p(
        "Modern packaged food retail is characterized by widespread utilization of synthetic chemical additives, "
        "preservatives, coloring agents, and flavor enhancers, many of which carry regulatory cautions or acute "
        "health risks for individuals with specific allergies, intolerances, or clinical dietary restrictions. "
        "While mandatory food labeling statutes require manufacturers to disclose ingredients, labels are frequently "
        "obscured by complex International Numbering System (INS) or E-number codes, microscopic typography, non-standard "
        "naming conventions, and physical distortions resulting from curved, reflective, or cylindrical packaging surfaces. "
        "Existing consumer applications rely either on barcode scanning linked to crowd-sourced databases—which fail "
        "when packaging reformulations occur—or attempt monolithic, unverified optical character recognition (OCR) "
        "models that suffer catastrophic degradation on non-planar packaging surfaces.",
        space_after=10
    )
    builder.add_p(
        "This project presents the design, architectural formulation, and empirical implementation of a Confidence-Aware "
        "Multimodal Food Label Verification System. The system addresses the limitations of monolithic verification by "
        "strictly decoupling product identification from ingredient-level dietary analysis into two distinct analytical "
        "pipelines. Pipeline A provides robust product identity resolution by extracting EAN-13 barcodes, verifying "
        "mathematical integrity via the Modulo-10 checksum algorithm, and querying the Open Food Facts international "
        "registry with an offline benchmark fallback catalog. Pipeline B executes comprehensive personal dietary analysis "
        "directly from packaging images using an advanced dual-configuration optical pipeline. Configuration A serves as "
        "an unaugmented baseline, while Configuration B introduces an 8-stage OpenCV image preprocessing pipeline "
        "incorporating aspect-ratio preserving rescaling, Laplacian variance blur detection, bilateral edge-preserving "
        "denoising, Contrast-Limited Adaptive Histogram Equalization (CLAHE), controlled unsharp masking, and adaptive "
        "Gaussian thresholding.",
        space_after=10
    )
    builder.add_p(
        "Extracted text is processed through an OCR normalization engine that corrects optical character substitutions "
        "(e.g., I→1, O→0) strictly within INS boundaries, enforces Codex Alimentarius range boundaries (100–1599), and "
        "maps detected tokens against an authoritative 750-entry INS taxonomy. A deterministic, rule-based preference engine "
        "evaluates detected additives and raw text against user dietary presets (Clean Eating, Strict Vegan, Allergen Sensitive, "
        "Low Additive) and 11 regulated allergen classes, generating a transparent suitability score from 0 to 100 with explicit "
        "point deductions. A 4-dimensional confidence vector drives an interactive Human-in-the-Loop (HITL) audit queue for "
        "unmapped tokens. The system was validated through an automated test suite comprising 187 comprehensive unit and "
        "integration tests across 13 functional modules, achieving a 100% pass rate. The application provides consumers with "
        "trustworthy, verifiable food safety analysis without black-box machine-learning hallucinations.",
        space_after=14
    )

    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.line_spacing = 1.3
    p_kw.paragraph_format.space_after = Pt(12)
    r_kwh = p_kw.add_run("Keywords: ")
    r_kwh.font.name = 'Times New Roman'
    r_kwh.font.size = Pt(11)
    r_kwh.bold = True
    r_kwt = p_kw.add_run(
        "Optical Character Recognition (OCR), Food Label Verification, International Numbering System (INS), "
        "Computer Vision Preprocessing, CLAHE, EAN-13 Checksum, Personalised Dietary Scoring, Multimodal Confidence Vector, "
        "Human-in-the-Loop Audit, Food Safety Informatics."
    )
    r_kwt.font.name = 'Times New Roman'
    r_kwt.font.size = Pt(11)
    r_kwt.italic = True

    # -----------------------------------------------------------------------
    # 6. TABLE OF CONTENTS
    # -----------------------------------------------------------------------
    doc.add_page_break()
    p_toc_head = doc.add_paragraph()
    p_toc_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_toc_head.paragraph_format.space_before = Pt(18)
    p_toc_head.paragraph_format.space_after = Pt(14)
    r_th = p_toc_head.add_run("TABLE OF CONTENTS")
    r_th.font.name = 'Times New Roman'
    r_th.font.size = Pt(15)
    r_th.bold = True
    r_th.font.color.rgb = RGBColor(0, 69, 74)

    toc_items = [
        ("Certificate of Institutional Approval", "ii"),
        ("Declaration of Originality", "iii"),
        ("Acknowledgements", "iv"),
        ("Abstract", "v"),
        ("List of Figures", "viii"),
        ("List of Tables", "ix"),
        ("List of Abbreviations", "x"),
        ("", ""),
        ("CHAPTER 1: INTRODUCTION", "1"),
        ("   1.1 Background of Packaged Food Labeling", "1"),
        ("   1.2 Evolution of Food Additive Regulation & International Standards", "2"),
        ("   1.3 Modern Consumer Health Challenges (Allergens, Lifestyle Diets)", "3"),
        ("   1.4 Problem Statement: The Gap in Automated Label Verification", "4"),
        ("   1.5 Research Motivation and Social Significance", "5"),
        ("   1.6 Project Objectives (Primary & Secondary)", "6"),
        ("   1.7 Scope and Operational Constraints (Decoupled Pipelines)", "6"),
        ("   1.8 Proposed Multimodal Engineering Methodology", "7"),
        ("   1.9 Organization and Structure of the Report", "8"),
        ("", ""),
        ("CHAPTER 2: LITERATURE SURVEY", "9"),
        ("   2.1 Introduction to Related Academic Research", "9"),
        ("   2.2 Optical Character Recognition on Packaging: State of the Art", "10"),
        ("   2.3 Machine Learning and Image Preprocessing for Complex Scenes", "11"),
        ("   2.4 Automated Product Identification Standards (GS1 EAN-13, OFF)", "12"),
        ("   2.5 International Additive Categorization Systems (INS, Codex, FSSAI)", "13"),
        ("   2.6 Personalised Decision Support Systems in Nutrition", "14"),
        ("   2.7 Critical Analysis of Baseline Paper: IEEE ICCCA 2025", "16"),
        ("   2.8 Comparative Analysis Matrix of Contemporary Food Tech Solutions", "17"),
        ("   2.9 Identified Research Gaps in Contemporary Systems", "19"),
        ("   2.10 Summary", "20"),
        ("", ""),
        ("CHAPTER 3: SYSTEM REQUIREMENTS AND ANALYSIS", "21"),
        ("   3.1 Analysis of Existing Manual & Commercial Solutions", "21"),
        ("   3.2 Limitations of Monolithic Verification Approaches", "22"),
        ("   3.3 Proposed Decoupled Multimodal System Architecture", "23"),
        ("   3.4 Comparative Advantages of the Proposed Solution", "24"),
        ("   3.5 Functional Requirements Specification (FRS)", "25"),
        ("   3.6 Non-Functional Requirements Specification (NFRS)", "26"),
        ("   3.7 Operational, Technical, and Economic Feasibility Study", "27"),
        ("   3.8 Hardware and Computational Environment Requirements", "28"),
        ("   3.9 Software Specifications, Libraries, and Technology Stack", "28"),
        ("   3.10 Comprehensive Use Case Specifications", "29"),
        ("", ""),
        ("CHAPTER 4: SYSTEM DESIGN AND ARCHITECTURAL MODELING", "30"),
        ("   4.1 Architectural Philosophy: Principles of Decoupled Multimodality", "30"),
        ("   4.2 High-Level System Architecture and Workflow", "31"),
        ("   4.3 Pipeline A: Product Identification Subsystem Design", "32"),
        ("   4.4 Pipeline B: Personalised Dietary Analysis Subsystem Design", "33"),
        ("   4.5 Optical Preprocessing Pipeline Design (Config A vs Config B)", "34"),
        ("   4.6 Frontend Component Hierarchy and State Management", "35"),
        ("   4.7 Backend Micro-Service and REST API Design", "36"),
        ("   4.8 Relational Database Architecture and Normalization (SQLite)", "37"),
        ("   4.9 Unified Modeling Language (UML) Structural and Behavioral Models", "38"),
        ("      4.9.1 Use Case Diagram", "39"),
        ("      4.9.2 Level-0 Context Diagram (DFD)", "40"),
        ("      4.9.3 Level-1 Data Flow Diagram (DFD)", "41"),
        ("      4.9.4 Level-2 Data Flow Diagram (Dietary Scoring)", "42"),
        ("      4.9.5 Entity-Relationship (ER) Diagram", "43"),
        ("      4.9.6 Sequence Diagram: Barcode Product Identification", "44"),
        ("      4.9.7 Sequence Diagram: Dietary Label Analysis", "44"),
        ("      4.9.8 Activity Diagram: HITL Audit Queue Workflow", "45"),
        ("      4.9.9 Component and Deployment Physical Model", "45"),
        ("", ""),
        ("CHAPTER 5: SYSTEM IMPLEMENTATION", "46"),
        ("   5.1 Development Environment Setup and Configuration", "46"),
        ("   5.2 Full-Stack Implementation Overview", "47"),
        ("   5.3 Authentication, Token Management, and PBKDF2 Password Hashing", "48"),
        ("   5.4 Barcode Decoding and Modulo-10 Checksum Algorithm Implementation", "49"),
        ("   5.5 Open Food Facts Integration with Offline Benchmark Fallback", "50"),
        ("   5.6 OpenCV Preprocessing Pipeline (Bilateral Filter, CLAHE, Sharpness)", "51"),
        ("   5.7 Dual-Configuration OCR Engine and Tesseract Integration", "53"),
        ("   5.8 Token Normalization, Typo Correction, and Regex Extraction", "54"),
        ("   5.9 INS Taxonomy Implementation (750 Curated Entries across 7 Classes)", "56"),
        ("   5.10 Dietary Preference Evaluation and Lifestyle Preset Matching", "57"),
        ("   5.11 Personalised Food Suitability Scoring Algorithm (0-100 Deductions)", "59"),
        ("   5.12 Multimodal Confidence Vector Formulation", "60"),
        ("   5.13 Regulatory Reference Cross-Checking Module (FSSAI, EFSA, Codex)", "61"),
        ("   5.14 Human-in-the-Loop (HITL) Audit Queue and Reviewer Workflow", "62"),
        ("   5.15 Historical Analysis Storage and Reporting Module", "63"),
        ("   5.16 User Interface Engineering: Minimalist Health-Tech Implementation", "64"),
        ("   5.17 REST API Implementation and HTTP Contract Catalog", "65"),
        ("", ""),
        ("CHAPTER 6: TESTING, VERIFICATION, AND PERFORMANCE EVALUATION", "66"),
        ("   6.1 Testing Methodology and Quality Assurance Strategy", "66"),
        ("   6.2 Unit Testing Framework and Execution Scope", "67"),
        ("   6.3 Integration and End-to-End Pipeline Verification", "68"),
        ("   6.4 Verification of the 187 Automated Test Cases (Full Pass Breakdown)", "69"),
        ("   6.5 API Endpoint Verification and HTTP Status Code Contracts", "71"),
        ("   6.6 Image Preprocessing Boundary Testing (Aspect Ratio, Blur Detection)", "72"),
        ("   6.7 Barcode Decoding and Checksum Validation Accuracy", "73"),
        ("   6.8 Database Integrity, Constraint, and Cascade Verification", "74"),
        ("   6.9 User Interface Usability, Accessibility, and Build Validation", "75"),
        ("   6.10 Empirical Execution Performance and Latency Metrics", "76"),
        ("   6.11 Detailed Test Case Execution Logs and Results Matrix", "76"),
        ("   6.12 Discussion of Results and Scientific Observations", "77"),
        ("", ""),
        ("CHAPTER 7: CONCLUSION AND FUTURE ENHANCEMENTS", "78"),
        ("   7.1 Conclusion", "78"),
        ("   7.2 Achievement of Project Objectives", "79"),
        ("   7.3 Summary of Contributions to Academic Food Informatics", "80"),
        ("   7.4 Technical Limitations of the Current Prototype", "80"),
        ("   7.5 Future Research Directions (Transformers, Multilingual OCR)", "81"),
        ("", ""),
        ("REFERENCES (IEEE Standard Bibliographic Citations)", "82"),
        ("", ""),
        ("PART C: RESEARCH PUBLICATION & PROFESSIONAL PLACEMENT", "87"),
        ("   Section C.1 Research Paper Publication Status & Manuscript Metadata", "87"),
        ("   Section C.2 Professional Placement Offer Letter / Internship Documents", "89")
    ]

    for title, pg in toc_items:
        if not title:
            p_space = doc.add_paragraph()
            p_space.paragraph_format.space_before = Pt(4)
            p_space.paragraph_format.space_after = Pt(4)
            continue
        p_row = doc.add_paragraph()
        p_row.paragraph_format.line_spacing = 1.15
        p_row.paragraph_format.space_after = Pt(2)
        r_t = p_row.add_run(title)
        r_t.font.name = 'Times New Roman'
        r_t.font.size = Pt(10.5)
        if "CHAPTER" in title or "PART" in title or "REFERENCES" in title:
            r_t.bold = True
            r_t.font.color.rgb = RGBColor(0, 69, 74)
        
        # Leader dots
        dots_count = max(4, 78 - len(title) - len(pg))
        r_dots = p_row.add_run(" " + "." * dots_count + " ")
        r_dots.font.name = 'Times New Roman'
        r_dots.font.size = Pt(9.5)
        r_dots.font.color.rgb = RGBColor(160, 160, 160)

        r_p = p_row.add_run(pg)
        r_p.font.name = 'Times New Roman'
        r_p.font.size = Pt(10.5)
        if "CHAPTER" in title or "PART" in title:
            r_p.bold = True

    # -----------------------------------------------------------------------
    # 7. LIST OF FIGURES
    # -----------------------------------------------------------------------
    doc.add_page_break()
    p_lof_head = doc.add_paragraph()
    p_lof_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lof_head.paragraph_format.space_before = Pt(18)
    p_lof_head.paragraph_format.space_after = Pt(14)
    r_lfh = p_lof_head.add_run("LIST OF FIGURES")
    r_lfh.font.name = 'Times New Roman'
    r_lfh.font.size = Pt(15)
    r_lfh.bold = True
    r_lfh.font.color.rgb = RGBColor(0, 69, 74)

    figures_list = [
        ("Figure 1.1", "Global Packaged Food Consumption and Additive Trends (2016–2027)", "3"),
        ("Figure 1.2", "Decoupled Multimodal Verification Methodology", "7"),
        ("Figure 2.1", "Taxonomy of Optical Character Recognition Approaches for Food Packaging", "10"),
        ("Figure 2.2", "Architectural Comparison: IEEE ICCCA 2025 Baseline vs. Proposed System", "16"),
        ("Figure 3.1", "Functional Decomposition Hierarchy of Proposed System", "24"),
        ("Figure 4.1", "Overall Decoupled Multimodal System Architecture", "31"),
        ("Figure 4.2", "Pipeline A: Barcode Detection, Modulo-10 Validation & Catalog Lookup Flowchart", "32"),
        ("Figure 4.3", "Pipeline B: Personalised Dietary Label Analysis & Scoring Flowchart", "33"),
        ("Figure 4.4", "Dual-Configuration OCR Architecture with Resilient Error Fallback", "34"),
        ("Figure 4.5", "OpenCV 8-Stage Image Enhancement Preprocessing Pipeline", "35"),
        ("Figure 4.6", "UML Use Case Diagram of Food Label Verification System", "39"),
        ("Figure 4.7", "Level-0 Context Data Flow Diagram (DFD)", "40"),
        ("Figure 4.8", "Level-1 Data Flow Diagram (DFD) of Major Subsystems", "41"),
        ("Figure 4.9", "Level-2 Detailed DFD for Additive Extraction and Personalised Scoring", "42"),
        ("Figure 4.10", "Relational Database Entity-Relationship (ER) Schema Diagram", "43"),
        ("Figure 4.11", "Sequence Diagram: Barcode Detection and External Verification", "44"),
        ("Figure 4.12", "Sequence Diagram: Personalised Dietary Label Analysis and Scoring", "44"),
        ("Figure 4.13", "Activity Diagram: Human-in-the-Loop (HITL) Audit Workflow", "45"),
        ("Figure 4.14", "Physical Deployment and Component Topology", "45"),
        ("Figure 5.1", "User Authentication and Registration Interface (Authentic UI)", "48"),
        ("Figure 5.2", "Health-Tech Wellness Dashboard Overview (Authentic UI)", "49"),
        ("Figure 5.3", "Dietary Preferences and Additive Avoidance Configuration (Authentic UI)", "57"),
        ("Figure 5.4", "Food Allergy Selection Grid (Authentic UI)", "58"),
        ("Figure 5.5", "Multimodal Product Scanning Interface (Authentic UI)", "64"),
        ("Figure 5.6", "Personalised Analysis Results and Circular Suitability Gauge (Authentic UI)", "64"),
        ("Figure 5.7", "Detected Ingredients Breakdown and Regulatory Justifications (Authentic UI)", "65"),
        ("Figure 5.8", "Advanced OCR Preprocessing Comparison Modal (Config A vs Config B) (Authentic UI)", "65"),
        ("Figure 5.9", "Scan History Management and Filtering Interface (Authentic UI)", "66"),
        ("Figure 5.10", "Human-in-the-Loop (HITL) Audit Queue Interface (Authentic UI)", "66"),
        ("Figure 6.1", "Distribution of 187 Passing Automated Tests Across Subsystems", "69"),
        ("Figure 6.2", "Preprocessing Latency vs. Resolution Scaling Curve", "76"),
        ("Figure 6.3", "OpenCV Preprocessing Stage-by-Stage Latency Breakdown", "76")
    ]

    for f_num, f_title, f_pg in figures_list:
        p_row = doc.add_paragraph()
        p_row.paragraph_format.line_spacing = 1.15
        p_row.paragraph_format.space_after = Pt(2)
        r_fn = p_row.add_run(f"{f_num}: {f_title}")
        r_fn.font.name = 'Times New Roman'
        r_fn.font.size = Pt(10)
        
        dots = max(4, 76 - len(f_num) - len(f_title) - len(f_pg))
        r_d = p_row.add_run(" " + "." * dots + " ")
        r_d.font.name = 'Times New Roman'
        r_d.font.size = Pt(9)
        r_d.font.color.rgb = RGBColor(160, 160, 160)

        r_pg = p_row.add_run(f_pg)
        r_pg.font.name = 'Times New Roman'
        r_pg.font.size = Pt(10)

    # -----------------------------------------------------------------------
    # 8. LIST OF TABLES
    # -----------------------------------------------------------------------
    doc.add_page_break()
    p_lot_head = doc.add_paragraph()
    p_lot_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lot_head.paragraph_format.space_before = Pt(18)
    p_lot_head.paragraph_format.space_after = Pt(14)
    r_lth = p_lot_head.add_run("LIST OF TABLES")
    r_lth.font.name = 'Times New Roman'
    r_lth.font.size = Pt(15)
    r_lth.bold = True
    r_lth.font.color.rgb = RGBColor(0, 69, 74)

    tables_list = [
        ("Table 1.1", "Primary and Secondary Objectives of the Investigation", "6"),
        ("Table 2.1", "Summary of Prior Research in OCR-Based Food Ingredient Extraction", "11"),
        ("Table 2.2", "Feature Matrix: Contemporary Food Label Solutions vs. Proposed System", "17"),
        ("Table 2.3", "Comparative Analysis against Baseline (Rawat et al., IEEE ICCCA 2025)", "18"),
        ("Table 3.1", "Deficiencies of Existing Food Verification Systems", "22"),
        ("Table 3.2", "Functional Requirements Specification (FRS) Summary", "25"),
        ("Table 3.3", "Non-Functional Requirements Specification (NFRS) Matrix", "26"),
        ("Table 3.4", "Hardware Development and Deployment Specifications", "28"),
        ("Table 3.5", "Software Dependencies and Technology Versions", "28"),
        ("Table 3.6", "Detailed Use Case Specification: Scanned Product Verification", "29"),
        ("Table 4.1", "Database Schema Specification: users Table", "37"),
        ("Table 4.2", "Database Schema Specification: auth_tokens Table", "37"),
        ("Table 4.3", "Database Schema Specification: dietary_profiles Table", "38"),
        ("Table 4.4", "Database Schema Specification: analysis_history Table", "38"),
        ("Table 4.5", "Database Indexing Catalog for Query Optimization", "38"),
        ("Table 5.1", "Implemented REST API Route Catalog and Endpoint Specifications", "47"),
        ("Table 5.2", "INS Additive Functional Category Mapping in Curated Taxonomy", "56"),
        ("Table 5.3", "Dietary Lifestyle Presets and Default Avoidance Configurations", "57"),
        ("Table 5.4", "Rule-Based Scoring Deduction Matrix and Hazard Weights", "59"),
        ("Table 5.5", "Specific Additive Regulatory Penalty Catalog", "60"),
        ("Table 5.6", "Multimodal Confidence Vector Component Definitions", "60"),
        ("Table 6.1", "Comprehensive Automated Test Suite Execution Summary (187 Tests)", "69"),
        ("Table 6.2", "Boundary Testing Results for OpenCV Preprocessor Module", "72"),
        ("Table 6.3", "EAN-13 Barcode Decoding and Checksum Validation Test Cases", "73"),
        ("Table 6.4", "Parser Token Extraction and False-Positive Suppression Evaluation", "74"),
        ("Table 6.5", "Execution Timing Metrics Across Core Backend Services", "76")
    ]

    for t_num, t_title, t_pg in tables_list:
        p_row = doc.add_paragraph()
        p_row.paragraph_format.line_spacing = 1.15
        p_row.paragraph_format.space_after = Pt(2)
        r_tn = p_row.add_run(f"{t_num}: {t_title}")
        r_tn.font.name = 'Times New Roman'
        r_tn.font.size = Pt(10)
        
        dots = max(4, 76 - len(t_num) - len(t_title) - len(t_pg))
        r_d = p_row.add_run(" " + "." * dots + " ")
        r_d.font.name = 'Times New Roman'
        r_d.font.size = Pt(9)
        r_d.font.color.rgb = RGBColor(160, 160, 160)

        r_pg = p_row.add_run(t_pg)
        r_pg.font.name = 'Times New Roman'
        r_pg.font.size = Pt(10)

    # -----------------------------------------------------------------------
    # 9. LIST OF ABBREVIATIONS
    # -----------------------------------------------------------------------
    doc.add_page_break()
    p_loa_head = doc.add_paragraph()
    p_loa_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_loa_head.paragraph_format.space_before = Pt(18)
    p_loa_head.paragraph_format.space_after = Pt(14)
    r_lah = p_loa_head.add_run("LIST OF ABBREVIATIONS")
    r_lah.font.name = 'Times New Roman'
    r_lah.font.size = Pt(15)
    r_lah.bold = True
    r_lah.font.color.rgb = RGBColor(0, 69, 74)

    abbreviations = [
        ("ADI", "Acceptable Daily Intake"),
        ("API", "Application Programming Interface"),
        ("BHA", "Butylated Hydroxyanisole (INS 320)"),
        ("BHT", "Butylated Hydroxytoluene (INS 321)"),
        ("CLAHE", "Contrast-Limited Adaptive Histogram Equalization"),
        ("Codex", "Codex Alimentarius Commission (FAO / WHO)"),
        ("CPU", "Central Processing Unit"),
        ("CSV", "Comma-Separated Values"),
        ("DFD", "Data Flow Diagram"),
        ("EAN", "European Article Number (GS1 Standard Barcode)"),
        ("EFSA", "European Food Safety Authority"),
        ("ER", "Entity-Relationship"),
        ("FSSAI", "Food Safety and Standards Authority of India"),
        ("GS1", "Global Standards 1 (International Barcode Authority)"),
        ("HFCS", "High-Fructose Corn Syrup"),
        ("HITL", "Human-in-the-Loop"),
        ("HTTP", "Hypertext Transfer Protocol"),
        ("HTTPS", "Hypertext Transfer Protocol Secure"),
        ("IARC", "International Agency for Research on Cancer"),
        ("INS", "International Numbering System for Food Additives"),
        ("JSON", "JavaScript Object Notation"),
        ("MCA", "Master of Computer Applications"),
        ("MITE", "Mangalore Institute of Technology and Engineering"),
        ("MSG", "Monosodium Glutamate (INS 621)"),
        ("NFRS", "Non-Functional Requirements Specification"),
        ("NLP", "Natural Language Processing"),
        ("OCR", "Optical Character Recognition"),
        ("OFF", "Open Food Facts (International Food Product Database)"),
        ("OpenCV", "Open Source Computer Vision Library"),
        ("PBKDF2", "Password-Based Key Derivation Function 2"),
        ("REST", "Representational State Transfer"),
        ("SHA", "Secure Hash Algorithm"),
        ("SPA", "Single Page Application (React)"),
        ("SQL", "Structured Query Language"),
        ("SQLite", "Self-Contained Serverless Relational Database Engine"),
        ("UML", "Unified Modeling Language"),
        ("USN", "University Seat Number"),
        ("VTU", "Visvesvaraya Technological University, Belagavi"),
        ("WER", "Word Error Rate"),
        ("WHO", "World Health Organization")
    ]

    for abbr, full in abbreviations:
        p_row = doc.add_paragraph()
        p_row.paragraph_format.line_spacing = 1.15
        p_row.paragraph_format.space_after = Pt(2)
        r_ab = p_row.add_run(f"{abbr:<12}")
        r_ab.font.name = 'Times New Roman'
        r_ab.font.size = Pt(10)
        r_ab.bold = True
        r_ab.font.color.rgb = RGBColor(0, 69, 74)
        
        r_f = p_row.add_run(f":  {full}")
        r_f.font.name = 'Times New Roman'
        r_f.font.size = Pt(10)

    print("Part A (Preliminary Pages) built successfully.")
