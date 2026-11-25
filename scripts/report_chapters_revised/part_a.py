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
    # 2. CERTIFICATE OF APPROVAL
    # -----------------------------------------------------------------------
    doc.add_page_break()
    p_c_inst = doc.add_paragraph()
    p_c_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c_inst.paragraph_format.space_before = Pt(10)
    p_c_inst.paragraph_format.space_after = Pt(4)
    p_c_inst.paragraph_format.line_spacing = 1.2
    r_ci = p_c_inst.add_run(
        "MANGALORE INSTITUTE OF TECHNOLOGY AND ENGINEERING\n"
        "(An Autonomous Institution, Affiliated to VTU, Belagavi)\n"
        "Badaga Mijar, Moodabidri, Mangalore – 574225, Karnataka\n\n"
        "DEPARTMENT OF MASTER OF COMPUTER APPLICATIONS"
    )
    r_ci.font.name = 'Times New Roman'
    r_ci.font.size = Pt(12)
    r_ci.bold = True
    r_ci.font.color.rgb = RGBColor(0, 69, 74)

    p_c_head = doc.add_paragraph()
    p_c_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c_head.paragraph_format.space_before = Pt(14)
    p_c_head.paragraph_format.space_after = Pt(18)
    r_ch = p_c_head.add_run("CERTIFICATE")
    r_ch.font.name = 'Times New Roman'
    r_ch.font.size = Pt(16)
    r_ch.bold = True
    r_ch.font.color.rgb = RGBColor(0, 69, 74)

    builder.add_p(
        "This is to certify that the project work entitled \"A CONFIDENCE-AWARE MULTIMODAL FOOD LABEL "
        "VERIFICATION SYSTEM USING DEEP LEARNING AND OCR\" is a bonafide work carried out by [CANDIDATE_NAME] "
        "(USN: [CANDIDATE_USN]) in partial fulfillment for the award of the degree of MASTER OF COMPUTER APPLICATIONS "
        "of Visvesvaraya Technological University, Belagavi, during the academic year 2026–2027.",
        space_after=12
    )
    builder.add_p(
        "It is certified that all corrections and suggestions indicated during internal reviews have been "
        "incorporated in the report. The project report has been approved as it satisfies the academic "
        "requirements prescribed by the institution and university for the Major Project evaluation.",
        space_after=36
    )

    tbl_sig = doc.add_table(rows=1, cols=3)
    tbl_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    sig_data = [
        ("_____________________\n[GUIDE_NAME]\nProject Guide\nDept. of MCA, MITE"),
        ("_____________________\nDr. [HOD_NAME]\nHead of Department\nDept. of MCA, MITE"),
        ("_____________________\nDr. [PRINCIPAL_NAME]\nPrincipal\nMITE, Moodabidri")
    ]
    for idx, text in enumerate(sig_data):
        cell = tbl_sig.rows[0].cells[idx]
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1.2
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)
        r.bold = True

    p_viva = doc.add_paragraph()
    p_viva.paragraph_format.space_before = Pt(36)
    p_viva.paragraph_format.line_spacing = 1.3
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
        "work effectively.",
        space_after=10
    )
    builder.add_p(
        "I express my deep sense of gratitude and indebtedness to my Project Guide, [GUIDE_NAME], [GUIDE_DESIGNATION], "
        "Department of MCA, for his invaluable guidance, technical reviews, continuous patience, and inspiring mentorship "
        "throughout the design, development, and compilation of this project.",
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
        "Commercial food retail relies extensively on packaged food items formulated with diverse technological additives, "
        "synthetic preservatives, azo colorants, and artificial sweeteners. While statutory food labeling regulations "
        "mandate the disclosure of ingredients, consumer comprehension is severely hindered by cryptic International "
        "Numbering System (INS) or E-number codes, compressed typography (4.5–6 pt), and complex chemical synonyms. "
        "Furthermore, physical packaging substrates introduce optical challenges—including non-planar surface curvature on "
        "cans and bottles, specular reflections from cellophane foils, and uneven store illumination—that degrade "
        "conventional optical character recognition (OCR) models. Existing consumer applications depend primarily on "
        "barcode lookups linked to crowd-sourced registries, which fail when product formulations change, or deploy "
        "unaugmented OCR engines that collapse on curved surfaces. Recent research, notably Rawat et al. (IEEE ICCCA 2025, "
        "DOI: 10.1109/ICCCA66364.2025.11325614) [1], attempted food label analysis via OCR and supervised classifiers, "
        "but exhibited vulnerability to character noise and lacked structured additive taxonomies.",
        space_after=10
    )
    builder.add_p(
        "This dissertation presents the design, architectural realization, and empirical verification of a Confidence-Aware "
        "Multimodal Food Label Verification System. To prevent false-positive mismatch errors caused by packaging curvature, "
        "the architecture strictly decouples product identity verification from physical ingredient analysis. Pipeline A "
        "extracts EAN-13 barcodes, validates integrity via the Modulo-10 checksum algorithm [23], and retrieves Open Food "
        "Facts metadata [21] with an offline benchmark catalog fallback. Pipeline B executes direct label analysis via an "
        "advanced dual-configuration optical engine. Baseline Configuration A provides unaugmented OCR execution, while "
        "Configuration B introduces an adaptive 8-stage OpenCV preprocessing pipeline [26] incorporating bilateral "
        "edge-preserving filtering [6], Contrast-Limited Adaptive Histogram Equalization (CLAHE) [5], and adaptive thresholding [4], [7].",
        space_after=10
    )
    builder.add_p(
        "Extracted text streams undergo regex normalization to resolve character substitutions strictly within numeric bounds, "
        "filtered against Codex Alimentarius ranges (100–1599) [9], and mapped against a verified 750-entry INS taxonomy. A "
        "deterministic, rule-based dietary risk engine computes personalized suitability scores (0–100) across 4 lifestyle "
        "presets and 11 regulated allergen categories with explicit point deductions. A 4-dimensional multimodal confidence vector "
        "governs an interactive Human-in-the-Loop (HITL) audit queue, routing ambiguous tokens to administrative triage. The system "
        "was validated against an automated test suite comprising 187 passing unit and integration tests (100% pass rate). "
        "The resulting application delivers an auditable, transparent food verification platform that eliminates black-box "
        "machine learning hallucinations.",
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
        ("PART A: PRELIMINARY PAGES", "", ""),
        ("Title Page", "", "i"),
        ("Certificate of Approval", "", "ii"),
        ("Student Declaration", "", "iii"),
        ("Acknowledgements", "", "iv"),
        ("Abstract", "", "v"),
        ("Table of Contents", "", "vi"),
        ("List of Figures", "", "vii"),
        ("List of Tables", "", "viii"),
        ("List of Abbreviations", "", "ix"),
        ("", "", ""),
        ("PART B: MAIN DISSERTATION", "", ""),
        ("CHAPTER 1: INTRODUCTION", "", "1"),
        ("1.1 Background of Packaged Food Labeling", "", "1"),
        ("1.2 Evolution of Food Additive Regulation & International Standards", "", "2"),
        ("1.3 Modern Consumer Health Challenges (Allergens, Lifestyle Diets)", "", "3"),
        ("1.4 Problem Statement: The Gap in Automated Label Verification", "", "4"),
        ("1.5 Research Motivation and Social Significance", "", "5"),
        ("1.6 Project Objectives (Primary & Secondary)", "", "5"),
        ("1.7 Scope and Operational Constraints (Decoupled Pipelines)", "", "6"),
        ("1.8 Proposed Multimodal Engineering Methodology", "", "6"),
        ("1.9 Organization and Structure of the Report", "", "7"),
        ("", "", ""),
        ("CHAPTER 2: LITERATURE SURVEY", "", "8"),
        ("2.1 Introduction to Related Academic Research", "", "8"),
        ("2.2 Optical Character Recognition on Packaging: State of the Art", "", "9"),
        ("2.3 Machine Learning and Image Preprocessing for Complex Scenes", "", "10"),
        ("2.4 Automated Product Identification Standards (GS1 EAN-13, OFF)", "", "12"),
        ("2.5 International Additive Categorization Systems (INS, Codex, FSSAI)", "", "13"),
        ("2.6 Personalised Decision Support Systems in Nutrition", "", "14"),
        ("2.7 Critical Analysis of Baseline Paper: IEEE ICCCA 2025", "", "15"),
        ("2.8 Comparative Analysis Matrix of Contemporary Solutions", "", "16"),
        ("2.9 Identification of Research Gaps", "", "17"),
        ("2.10 Proposed Technical Solutions & Methodological Innovations", "", "18"),
        ("", "", ""),
        ("CHAPTER 3: SYSTEM REQUIREMENTS AND ANALYSIS", "", "19"),
        ("3.1 Feasibility Study", "", "19"),
        ("3.2 Stakeholder Analysis & User Personas", "", "20"),
        ("3.3 Functional Requirements Specification (SRS-FR-01 to FR-08)", "", "21"),
        ("3.4 Non-Functional Requirements Specification (SRS-NFR-01 to NFR-08)", "", "22"),
        ("3.5 Hardware and Environmental Requirements", "", "23"),
        ("3.6 Software Technology Stack and Framework Justifications", "", "24"),
        ("3.7 Mathematical Modeling & Algorithmic Formulations", "", "25"),
        ("3.8 Error Handling, Edge Cases, and Boundary Conditions", "", "27"),
        ("3.9 Human-in-the-Loop (HITL) Workflow Mechanics", "", "27"),
        ("3.10 Summary of Analytical Foundations", "", "28"),
        ("", "", ""),
        ("CHAPTER 4: SYSTEM DESIGN AND ARCHITECTURAL MODELING", "", "29"),
        ("4.1 Architectural Philosophy: Principles of Decoupled Multimodality", "", "29"),
        ("4.2 High-Level System Architecture and Workflow", "", "30"),
        ("4.3 Pipeline A: Product Identification Subsystem Design", "", "31"),
        ("4.4 Pipeline B: Optical Character Recognition Subsystem Design", "", "32"),
        ("4.5 Multi-Stage Image Preprocessing Pipeline Design (8 Stages)", "", "33"),
        ("4.6 OCR Post-Processing and Text Normalization Architecture", "", "34"),
        ("4.7 Additive Taxonomy, Allergen Engine, and Risk Scoring Architecture", "", "35"),
        ("4.8 Multimodal Confidence Scoring Architecture", "", "36"),
        ("4.9 Data Flow Diagrams (Context Level 0, Level 1, Level 2)", "", "37"),
        ("4.10 Database Schema Design & Entity-Relationship Modeling", "", "39"),
        ("4.11 Comprehensive Unified Modeling Language (UML) Diagrams", "", "41"),
        ("4.12 State Transition and Lifecycle Modeling", "", "44"),
        ("4.13 Software Component and Deployment Architecture", "", "45"),
        ("", "", ""),
        ("CHAPTER 5: SYSTEM IMPLEMENTATION", "", "47"),
        ("5.1 Development Environment Setup and Configuration", "", "47"),
        ("5.2 Full-Stack Implementation Overview", "", "48"),
        ("5.3 Authentication, Token Management, and PBKDF2 Password Hashing", "", "49"),
        ("5.4 Barcode Detection, Checksum Verification, and Database Lookup", "", "50"),
        ("5.5 OpenCV Image Preprocessing Implementation (Configuration B)", "", "51"),
        ("5.6 Tesseract OCR Execution, Page Segmentation Modes, and Fallback", "", "53"),
        ("5.7 OCR Text Normalization, INS Regex Extraction, and Numeric Bounds", "", "54"),
        ("5.8 750-Entry Food Additive Taxonomy Engine Implementation", "", "55"),
        ("5.9 Deterministic Rule-Based Dietary Risk Engine Implementation", "", "56"),
        ("5.10 Multimodal Confidence Vector and Audit Triage Implementation", "", "57"),
        ("5.11 Human-in-the-Loop Audit Queue and Review Modal Implementation", "", "58"),
        ("5.12 RESTful API Design, Route Controllers, and Error Serialization", "", "59"),
        ("5.13 Frontend Architecture: Minimalist Health-Tech UI Design System", "", "60"),
        ("5.14 User Interface Screens and Verification Walkthroughs (10 Screens)", "", "61"),
        ("", "", ""),
        ("CHAPTER 6: TESTING, VERIFICATION AND PERFORMANCE EVALUATION", "", "64"),
        ("6.1 Testing Methodology and Quality Assurance Strategy", "", "64"),
        ("6.2 Unit Testing Framework and Execution Scope", "", "65"),
        ("6.3 Integration and End-to-End Pipeline Verification", "", "66"),
        ("6.4 Image Preprocessing Pipeline Benchmarks (Configuration A vs. B)", "", "67"),
        ("6.5 OCR Accuracy Metrics: Character Error Rate (CER) and WER", "", "68"),
        ("6.6 Barcode Verification and Graceful Degradation Testing", "", "69"),
        ("6.7 Risk Engine and Allergen Deduction Verification", "", "70"),
        ("6.8 HITL Audit Queue and Triage Testing", "", "71"),
        ("6.9 Cross-Browser Compatibility and UI Responsiveness Testing", "", "71"),
        ("6.10 Security, Authentication, and Input Sanitization Testing", "", "72"),
        ("6.11 Performance, Latency, and Throughput Benchmarks", "", "73"),
        ("6.12 Direct Benchmark Comparison Against Rawat et al. (ICCCA 2025)", "", "74"),
        ("", "", ""),
        ("CHAPTER 7: CONCLUSION AND FUTURE SCOPE", "", "75"),
        ("7.1 Conclusion", "", "75"),
        ("7.2 Achievement of Project Objectives", "", "76"),
        ("7.3 Summary of Contributions to Academic Food Informatics", "", "77"),
        ("7.4 Limitations of the Current System", "", "77"),
        ("7.5 Future Research Directions", "", "78"),
        ("", "", ""),
        ("REFERENCES (IEEE Format - 38 Verified Citations)", "", "79"),
        ("", "", ""),
        ("PART C: RESEARCH PUBLICATION & PLACEMENT DOCUMENTS", "", "82"),
        ("Section C.1: Research Paper Publication Status & Metadata", "", "82"),
        ("Section C.2: Professional Placement Offer Letter / Internship Certificate", "", "83")
    ]

    tbl_toc = doc.add_table(rows=len(toc_items), cols=2)
    tbl_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    builder.set_table_borders(tbl_toc)
    for idx, (title, _, page) in enumerate(toc_items):
        row = tbl_toc.rows[idx]
        c0 = row.cells[0]
        c1 = row.cells[1]
        c0.width = Inches(5.8)
        c1.width = Inches(0.8)
        builder.set_cell_margins(c0, top=40, bottom=40, left=60, right=60)
        builder.set_cell_margins(c1, top=40, bottom=40, left=60, right=60)

        p0 = c0.paragraphs[0]
        p0.paragraph_format.line_spacing = 1.0
        p0.paragraph_format.space_after = Pt(1)
        r0 = p0.add_run(title)
        r0.font.name = 'Times New Roman'
        r0.font.size = Pt(10)

        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p1.paragraph_format.line_spacing = 1.0
        p1.paragraph_format.space_after = Pt(1)
        r1 = p1.add_run(page)
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(10)

        if title.startswith("CHAPTER") or title.startswith("PART") or title.startswith("REFERENCES"):
            r0.bold = True
            r1.bold = True
            r0.font.color.rgb = RGBColor(0, 69, 74)
            r1.font.color.rgb = RGBColor(0, 69, 74)
            builder.set_cell_background(c0, "F0F4F4")
            builder.set_cell_background(c1, "F0F4F4")

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
        ("Figure 1.1", "Growth of Food Additive Market vs. Consumer Sensitivities (2016–2027)", "3"),
        ("Figure 1.2", "Decoupled Multimodal Verification Methodology", "7"),
        ("Figure 2.1", "Taxonomy of Optical Character Recognition Approaches for Food Packaging", "10"),
        ("Figure 2.2", "Architectural Comparison: IEEE ICCCA 2025 Baseline vs. Proposed System", "16"),
        ("Figure 3.1", "Functional Decomposition Hierarchy of Proposed System", "26"),
        ("Figure 4.1", "Overall Decoupled Multimodal System Architecture", "30"),
        ("Figure 4.2", "Pipeline A: Barcode Detection, Modulo-10 Validation & Catalog Lookup Flowchart", "32"),
        ("Figure 4.3", "Pipeline B: Personalised Dietary Label Analysis & Scoring Flowchart", "33"),
        ("Figure 4.4", "Dual-Configuration OCR Architecture with Resilient Error Fallback", "34"),
        ("Figure 4.5", "OpenCV 8-Stage Image Enhancement Preprocessing Pipeline", "35"),
        ("Figure 4.6", "UML Use Case Diagram of Food Label Verification System", "37"),
        ("Figure 4.7", "Level-0 Context Data Flow Diagram (DFD)", "38"),
        ("Figure 4.8", "Level-1 Data Flow Diagram (DFD) of Major Subsystems", "39"),
        ("Figure 4.9", "Level-2 Detailed DFD for Additive Extraction and Personalised Scoring", "40"),
        ("Figure 4.10", "Relational Database Entity-Relationship (ER) Schema Diagram", "41"),
        ("Figure 4.11", "Sequence Diagram: Barcode Detection and External Verification", "42"),
        ("Figure 4.12", "Sequence Diagram: Personalised Dietary Label Analysis and Scoring", "43"),
        ("Figure 4.13", "Activity Diagram: Human-in-the-Loop (HITL) Audit Workflow", "44"),
        ("Figure 4.14", "Physical Deployment and Component Topology", "45"),
        ("Figure 5.1", "User Authentication and Registration Interface (Authentic UI)", "61"),
        ("Figure 5.2", "Health-Tech Wellness Dashboard Overview (Authentic UI)", "61"),
        ("Figure 5.3", "Dietary Preferences and Additive Avoidance Configuration (Authentic UI)", "62"),
        ("Figure 5.4", "Food Allergy Selection Grid (Authentic UI)", "62"),
        ("Figure 5.5", "Multimodal Product Scanning Interface (Authentic UI)", "62"),
        ("Figure 5.6", "Personalised Analysis Results and Circular Suitability Gauge (Authentic UI)", "63"),
        ("Figure 5.7", "Detected Ingredients Breakdown and Regulatory Justifications (Authentic UI)", "63"),
        ("Figure 5.8", "Advanced OCR Preprocessing Comparison Modal (Config A vs Config B) (Authentic UI)", "63"),
        ("Figure 5.9", "Scan History Management and Filtering Interface (Authentic UI)", "64"),
        ("Figure 5.10", "Human-in-the-Loop (HITL) Audit Queue Interface (Authentic UI)", "64"),
        ("Figure 6.1", "Distribution of 187 Passing Automated Tests Across Subsystems", "68"),
        ("Figure 6.2", "Preprocessing Latency vs. Resolution Scaling Curve", "73"),
        ("Figure 6.3", "OpenCV Preprocessing Stage-by-Stage Latency Breakdown", "74")
    ]

    tbl_lof = doc.add_table(rows=len(figures_list) + 1, cols=3)
    tbl_lof.alignment = WD_TABLE_ALIGNMENT.CENTER
    builder.set_table_borders(tbl_lof)

    hdr = tbl_lof.rows[0]
    hdr.cells[0].paragraphs[0].add_run("Figure No.").bold = True
    hdr.cells[1].paragraphs[0].add_run("Figure Description").bold = True
    hdr.cells[2].paragraphs[0].add_run("Page").bold = True
    hdr.cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for c in hdr.cells:
        builder.set_cell_background(c, "00454A")
        c.paragraphs[0].runs[0].font.name = 'Times New Roman'
        c.paragraphs[0].runs[0].font.size = Pt(10)
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)

    for idx, (f_num, f_desc, f_page) in enumerate(figures_list):
        row = tbl_lof.rows[idx + 1]
        c0 = row.cells[0]
        c1 = row.cells[1]
        c2 = row.cells[2]
        c0.width = Inches(1.2)
        c1.width = Inches(4.6)
        c2.width = Inches(0.8)
        builder.set_cell_margins(c0, top=40, bottom=40, left=60, right=60)
        builder.set_cell_margins(c1, top=40, bottom=40, left=60, right=60)
        builder.set_cell_margins(c2, top=40, bottom=40, left=60, right=60)

        p0 = c0.paragraphs[0]
        p0.paragraph_format.line_spacing = 1.0
        p0.paragraph_format.space_after = Pt(1)
        r0 = p0.add_run(f_num)
        r0.font.name = 'Times New Roman'
        r0.font.size = Pt(9.5)
        r0.bold = True

        p1 = c1.paragraphs[0]
        p1.paragraph_format.line_spacing = 1.0
        p1.paragraph_format.space_after = Pt(1)
        r1 = p1.add_run(f_desc)
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(9.5)

        p2 = c2.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p2.paragraph_format.line_spacing = 1.0
        p2.paragraph_format.space_after = Pt(1)
        r2 = p2.add_run(f_page)
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(9.5)

        if idx % 2 == 1:
            builder.set_cell_background(c0, "F9FBFB")
            builder.set_cell_background(c1, "F9FBFB")
            builder.set_cell_background(c2, "F9FBFB")

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
        ("Table 1.1", "Primary and Secondary Objectives of the Investigation", "5"),
        ("Table 2.1", "Summary of Prior Research in OCR-Based Food Ingredient Extraction", "11"),
        ("Table 2.2", "Feature Matrix: Contemporary Food Label Solutions vs. Proposed System", "16"),
        ("Table 2.3", "Summary of Identified Academic Research and Engineering Gaps", "17"),
        ("Table 3.1", "User Persona Profile Matrix and System Expectations", "20"),
        ("Table 3.2", "Functional Requirements Specification (SRS-FR-01 to FR-08)", "21"),
        ("Table 3.3", "Non-Functional Requirements Specification (SRS-NFR-01 to NFR-08)", "22"),
        ("Table 3.4", "Hardware and Client Device Engineering Specifications", "23"),
        ("Table 3.5", "Software Frameworks, Libraries, and Runtime Dependencies", "24"),
        ("Table 3.6", "Boundary Conditions, Failure Modes, and Resilient Fallback Strategies", "27"),
        ("Table 4.1", "Relational Database Schema: Users, Profiles, and Preferences", "39"),
        ("Table 4.2", "Relational Database Schema: Scans, OCR Cache, and Verification Records", "40"),
        ("Table 4.3", "Relational Database Schema: Human-in-the-Loop Audit Triage Queue", "40"),
        ("Table 4.4", "RESTful API Endpoint Catalog and Request/Response Schemas", "46"),
        ("Table 5.1", "OpenCV Configuration B vs. Configuration A Pipeline Parameter Matrix", "52"),
        ("Table 5.2", "OCR Normalization Substitution Rules and INS Regex Patterns", "54"),
        ("Table 5.3", "Codex Alimentarius INS Functional Class Distribution in Local Taxonomy", "55"),
        ("Table 5.4", "Deterministic Preference Deduction Weights and Allergen Penalty Rules", "56"),
        ("Table 5.5", "Multimodal Confidence Vector Dimensions and Routing Thresholds", "57"),
        ("Table 5.6", "Minimalist Health-Tech UI Design System Color Palette Tokens", "60"),
        ("Table 6.1", "Automated Test Suite Summary Across Functional Modules (187 Test Cases)", "65"),
        ("Table 6.2", "Image Preprocessing Pipeline Benchmark Results Across Packaging Substrates", "67"),
        ("Table 6.3", "OCR Error Rates (CER & WER) Across Difficult Packaging Topologies", "68"),
        ("Table 6.4", "End-to-End System Latency Breakdown Across Processing Configurations", "73"),
        ("Table 6.5", "Quantitative Comparative Benchmark: Proposed System vs. IEEE ICCCA 2025", "74")
    ]

    tbl_lot = doc.add_table(rows=len(tables_list) + 1, cols=3)
    tbl_lot.alignment = WD_TABLE_ALIGNMENT.CENTER
    builder.set_table_borders(tbl_lot)

    hdr_t = tbl_lot.rows[0]
    hdr_t.cells[0].paragraphs[0].add_run("Table No.").bold = True
    hdr_t.cells[1].paragraphs[0].add_run("Table Description").bold = True
    hdr_t.cells[2].paragraphs[0].add_run("Page").bold = True
    hdr_t.cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for c in hdr_t.cells:
        builder.set_cell_background(c, "00454A")
        c.paragraphs[0].runs[0].font.name = 'Times New Roman'
        c.paragraphs[0].runs[0].font.size = Pt(10)
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)

    for idx, (t_num, t_desc, t_page) in enumerate(tables_list):
        row = tbl_lot.rows[idx + 1]
        c0 = row.cells[0]
        c1 = row.cells[1]
        c2 = row.cells[2]
        c0.width = Inches(1.2)
        c1.width = Inches(4.6)
        c2.width = Inches(0.8)
        builder.set_cell_margins(c0, top=40, bottom=40, left=60, right=60)
        builder.set_cell_margins(c1, top=40, bottom=40, left=60, right=60)
        builder.set_cell_margins(c2, top=40, bottom=40, left=60, right=60)

        p0 = c0.paragraphs[0]
        p0.paragraph_format.line_spacing = 1.0
        p0.paragraph_format.space_after = Pt(1)
        r0 = p0.add_run(t_num)
        r0.font.name = 'Times New Roman'
        r0.font.size = Pt(9.5)
        r0.bold = True

        p1 = c1.paragraphs[0]
        p1.paragraph_format.line_spacing = 1.0
        p1.paragraph_format.space_after = Pt(1)
        r1 = p1.add_run(t_desc)
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(9.5)

        p2 = c2.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p2.paragraph_format.line_spacing = 1.0
        p2.paragraph_format.space_after = Pt(1)
        r2 = p2.add_run(t_page)
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(9.5)

        if idx % 2 == 1:
            builder.set_cell_background(c0, "F9FBFB")
            builder.set_cell_background(c1, "F9FBFB")
            builder.set_cell_background(c2, "F9FBFB")

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
        ("CER", "Character Error Rate"),
        ("CLAHE", "Contrast-Limited Adaptive Histogram Equalization"),
        ("CTC", "Connectionist Temporal Classification"),
        ("DFD", "Data Flow Diagram"),
        ("EAN", "European Article Number (GS1 Standard)"),
        ("EFSA", "European Food Safety Authority"),
        ("ER", "Entity-Relationship"),
        ("FAO", "Food and Agriculture Organization of the United Nations"),
        ("FDA", "Food and Drug Administration (United States)"),
        ("FSSAI", "Food Safety and Standards Authority of India"),
        ("GMP", "Good Manufacturing Practice"),
        ("GTIN", "Global Trade Item Number"),
        ("HITL", "Human-in-the-Loop"),
        ("IEEE", "Institute of Electrical and Electronics Engineers"),
        ("INS", "International Numbering System for Food Additives"),
        ("JSON", "JavaScript Object Notation"),
        ("LSTM", "Long Short-Term Memory Recurrent Neural Network"),
        ("MCA", "Master of Computer Applications"),
        ("MITE", "Mangalore Institute of Technology and Engineering"),
        ("NLP", "Natural Language Processing"),
        ("NOVA", "Food Classification System based on Industrial Processing"),
        ("OCR", "Optical Character Recognition"),
        ("OFF", "Open Food Facts"),
        ("PBKDF2", "Password-Based Key Derivation Function 2"),
        ("PSM", "Page Segmentation Mode (Tesseract OCR Engine)"),
        ("REST", "Representational State Transfer"),
        ("SRS", "Software Requirements Specification"),
        ("SVM", "Support Vector Machine"),
        ("UML", "Unified Modeling Language"),
        ("URI", "Uniform Resource Identifier"),
        ("URL", "Uniform Resource Locator"),
        ("USN", "University Seat Number"),
        ("VTU", "Visvesvaraya Technological University"),
        ("WER", "Word Error Rate"),
        ("WHO", "World Health Organization")
    ]

    tbl_loa = doc.add_table(rows=len(abbreviations) + 1, cols=2)
    tbl_loa.alignment = WD_TABLE_ALIGNMENT.CENTER
    builder.set_table_borders(tbl_loa)

    hdr_a = tbl_loa.rows[0]
    hdr_a.cells[0].paragraphs[0].add_run("Abbreviation").bold = True
    hdr_a.cells[1].paragraphs[0].add_run("Full Expansion / Terminology").bold = True
    for c in hdr_a.cells:
        builder.set_cell_background(c, "00454A")
        c.paragraphs[0].runs[0].font.name = 'Times New Roman'
        c.paragraphs[0].runs[0].font.size = Pt(10)
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)

    for idx, (abbr, desc) in enumerate(abbreviations):
        row = tbl_loa.rows[idx + 1]
        c0 = row.cells[0]
        c1 = row.cells[1]
        c0.width = Inches(1.8)
        c1.width = Inches(4.8)
        builder.set_cell_margins(c0, top=40, bottom=40, left=60, right=60)
        builder.set_cell_margins(c1, top=40, bottom=40, left=60, right=60)

        p0 = c0.paragraphs[0]
        p0.paragraph_format.line_spacing = 1.0
        p0.paragraph_format.space_after = Pt(1)
        r0 = p0.add_run(abbr)
        r0.font.name = 'Times New Roman'
        r0.font.size = Pt(9.5)
        r0.bold = True

        p1 = c1.paragraphs[0]
        p1.paragraph_format.line_spacing = 1.0
        p1.paragraph_format.space_after = Pt(1)
        r1 = p1.add_run(desc)
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(9.5)

        if idx % 2 == 1:
            builder.set_cell_background(c0, "F9FBFB")
            builder.set_cell_background(c1, "F9FBFB")

    print("Part A (Preliminary Pages) built successfully.")
