"""
build_report_with_spaces.py
===========================
Compiles the complete MCA Major Project Report into an editable Word document
and PDF with reserved bordered spaces for diagrams and output screenshots,
following strictly the MITE Institutional Thesis Guide format (80-90 Pages).

Target Deliverables:
- d:\\food-risk-checker\\final_report\\MCA_Project_Report_80Pages_Text_Draft.docx
- d:\\food-risk-checker\\final_report\\MCA_Project_Report_80Pages_Text_Draft.pdf
"""

import os
import sys
import docx
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

SCRIPTS_DIR = r"d:\food-risk-checker\scripts"
sys.path.insert(0, SCRIPTS_DIR)
sys.path.insert(0, os.path.join(SCRIPTS_DIR, "report_chapters_revised"))

from report_chapters_revised.part_a import build_part_a
from report_chapters_revised.chapter_1 import build_chapter_1
from report_chapters_revised.chapter_2 import build_chapter_2
from report_chapters_revised.chapter_3 import build_chapter_3
from report_chapters_revised.chapter_4 import build_chapter_4
from report_chapters_revised.chapter_5 import build_chapter_5
from report_chapters_revised.chapter_6 import build_chapter_6
from report_chapters_revised.chapter_7 import build_chapter_7_and_refs

REPORT_DIR = r"d:\food-risk-checker\final_report"
DRAFT_DOCX_PATH = os.path.join(REPORT_DIR, "MCA_Project_Report_80Pages_Text_Draft.docx")
DRAFT_PDF_PATH = os.path.join(REPORT_DIR, "MCA_Project_Report_80Pages_Text_Draft.pdf")

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_background(cell, color_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_table_borders(table, color="D3D3D3"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def set_box_borders(table, color="999999"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="6" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="single" w:sz="6" w:space="0" w:color="{color}"/>'
        f'<w:right w:val="single" w:sz="6" w:space="0" w:color="{color}"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def add_page_number_field(run):
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = 'PAGE'
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')
    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'end')
    r = run._r
    r.append(fldChar1)
    r.append(instrText)
    r.append(fldChar2)
    r.append(fldChar3)

class MiteReportBuilderWithSpaces:
    def __init__(self):
        self.doc = docx.Document()
        self._configure_default_styles()

    def set_cell_margins(self, cell, top=100, bottom=100, left=150, right=150):
        set_cell_margins(cell, top, bottom, left, right)

    def set_cell_background(self, cell, color_hex):
        set_cell_background(cell, color_hex)

    def set_table_borders(self, table, color="D3D3D3"):
        set_table_borders(table, color)

    def _configure_default_styles(self):
        style_normal = self.doc.styles['Normal']
        style_normal.font.name = 'Times New Roman'
        style_normal.font.size = Pt(12)
        style_normal.font.color.rgb = RGBColor(17, 17, 17)
        style_normal.paragraph_format.line_spacing = 1.5
        style_normal.paragraph_format.space_after = Pt(6)
        style_normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    def configure_section_margins(self, section, is_part_a=False):
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)
        section.left_margin = Cm(3.5)  # 3.5 cm left binding margin
        section.right_margin = Cm(2.54)
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)

        sectPr = section._sectPr
        pgNumType = OxmlElement('w:pgNumType')
        if is_part_a:
            pgNumType.set(qn('w:fmt'), 'lowerRoman')
        else:
            pgNumType.set(qn('w:fmt'), 'decimal')
            pgNumType.set(qn('w:start'), '1')
        sectPr.append(pgNumType)

        footer = section.footer
        p = footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run()
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(100, 100, 100)
        add_page_number_field(run)

    def add_p(self, text, space_after=6, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
        p = self.doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(space_after)
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.bold = bold
        run.italic = italic
        return p

    def add_chapter_title(self, chapter_num, title):
        self.doc.add_page_break()
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(22)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.line_spacing = 1.0
        run = p.add_run(f"CHAPTER {chapter_num}\n{title.upper()}")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(16)
        run.bold = True
        run.font.color.rgb = RGBColor(0, 69, 74)

        p_rule = self.doc.add_paragraph()
        p_rule.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_rule.paragraph_format.space_after = Pt(18)
        p_rule.paragraph_format.line_spacing = 1.0
        run_rule = p_rule.add_run("―" * 38)
        run_rule.font.name = 'Times New Roman'
        run_rule.font.size = Pt(10)
        run_rule.font.color.rgb = RGBColor(150, 150, 150)

    def add_h1(self, text):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.line_spacing = 1.2
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.bold = True
        run.font.color.rgb = RGBColor(0, 69, 74)
        return p

    def add_h2(self, text):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.2
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.bold = True
        run.font.color.rgb = RGBColor(17, 17, 17)
        return p

    def add_h3(self, text):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.2
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.bold = True
        run.italic = True
        return p

    def add_table(self, title_text, headers, data, col_widths=None):
        p_title = self.doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_title.paragraph_format.space_before = Pt(10)
        p_title.paragraph_format.space_after = Pt(4)
        p_title.paragraph_format.keep_with_next = True
        run_t = p_title.add_run(title_text)
        run_t.font.name = 'Times New Roman'
        run_t.font.size = Pt(10)
        run_t.bold = True

        tbl = self.doc.add_table(rows=len(data) + 1, cols=len(headers))
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(tbl)

        hdr_row = tbl.rows[0]
        for i, h_text in enumerate(headers):
            cell = hdr_row.cells[i]
            set_cell_margins(cell, top=120, bottom=120, left=150, right=150)
            set_cell_background(cell, "00454A")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(h_text)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9.5)
            r.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)

        for r_idx, row_vals in enumerate(data):
            row = tbl.rows[r_idx + 1]
            bg_col = "F9FBFB" if r_idx % 2 == 1 else "FFFFFF"
            for c_idx, val in enumerate(row_vals):
                cell = row.cells[c_idx]
                set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
                set_cell_background(cell, bg_col)
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx != 0 else WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.line_spacing = 1.0
                p.paragraph_format.space_after = Pt(0)
                r = p.add_run(str(val))
                r.font.name = 'Times New Roman'
                r.font.size = Pt(9)

        if col_widths:
            for row in tbl.rows:
                for idx, w in enumerate(col_widths):
                    row.cells[idx].width = w

        p_after = self.doc.add_paragraph()
        p_after.paragraph_format.space_before = Pt(4)
        p_after.paragraph_format.space_after = Pt(4)

    def add_figure(self, caption_text, img_filename, width_inches=4.8):
        """
        Leaves a dedicated bordered placeholder space/box for diagrams and output screenshots,
        followed by the standard 10pt bold centered caption below.
        """
        # Determine appropriate reserved height based on figure type
        if "fig_5_" in img_filename:
            height_in = 3.0  # UI screenshots
        elif "fig_4_" in img_filename:
            height_in = 2.8  # Architecture & UML diagrams
        else:
            height_in = 2.5  # General diagrams & charts

        tbl = self.doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.rows[0].height = Inches(height_in)
        set_box_borders(tbl, color="B8C4C4")

        cell = tbl.cell(0, 0)
        cell.width = Inches(5.6)
        set_cell_margins(cell, top=120, bottom=120, left=150, right=150)
        set_cell_background(cell, "FAFCFC")

        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        # Vertical centering simulation via space_before
        p.paragraph_format.space_before = Pt(int(height_in * 72 / 2 - 20))
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.2

        r_box_icon = p.add_run("┌──────────────────────────────────────────────────────────┐\n")
        r_box_icon.font.name = 'Courier New'
        r_box_icon.font.size = Pt(8.5)
        r_box_icon.font.color.rgb = RGBColor(160, 160, 160)

        r_box = p.add_run(f" [ SPACE RESERVED FOR DIAGRAM / OUTPUT SCREENSHOT ]\n")
        r_box.font.name = 'Times New Roman'
        r_box.font.size = Pt(10)
        r_box.bold = True
        r_box.font.color.rgb = RGBColor(0, 69, 74)

        r_box_sub = p.add_run(f"Reference Asset: {img_filename} (Format: Scalable Vector / 300 DPI)\n")
        r_box_sub.font.name = 'Times New Roman'
        r_box_sub.font.size = Pt(8.5)
        r_box_sub.font.color.rgb = RGBColor(120, 120, 120)
        r_box_sub.italic = True

        r_box_icon2 = p.add_run("└──────────────────────────────────────────────────────────┘")
        r_box_icon2.font.name = 'Courier New'
        r_box_icon2.font.size = Pt(8.5)
        r_box_icon2.font.color.rgb = RGBColor(160, 160, 160)

        # Caption BELOW figure (10pt bold centered)
        p_cap = self.doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(4)
        p_cap.paragraph_format.space_after = Pt(12)
        run_cap = p_cap.add_run(caption_text)
        run_cap.font.name = 'Times New Roman'
        run_cap.font.size = Pt(10)
        run_cap.bold = True

def main():
    print("=" * 70)
    print("BUILDING 80-PAGE MCA REPORT WITH RESERVED SPACES FOR DIAGRAMS")
    print("=" * 70)

    builder = MiteReportBuilderWithSpaces()

    print("Building Part A: Preliminary Pages...")
    build_part_a(builder)

    print("Building Chapter 1: Introduction...")
    build_chapter_1(builder)

    print("Building Chapter 2: Literature Survey...")
    build_chapter_2(builder)

    print("Building Chapter 3: System Requirements & Analysis...")
    build_chapter_3(builder)

    print("Building Chapter 4: System Design & Architectural Modeling...")
    build_chapter_4(builder)

    print("Building Chapter 5: System Implementation...")
    build_chapter_5(builder)

    print("Building Chapter 6: Testing, Verification & Performance Evaluation...")
    build_chapter_6(builder)

    print("Building Chapter 7: Conclusion & Future Scope + References + Part C...")
    build_chapter_7_and_refs(builder)

    print(f"Saving compiled DOCX to {DRAFT_DOCX_PATH}...")
    builder.doc.save(DRAFT_DOCX_PATH)
    print("Draft DOCX with diagram spaces built successfully!")
    print(f"Master DOCX File Size: {os.path.getsize(DRAFT_DOCX_PATH) / 1024:.2f} KB")

if __name__ == "__main__":
    main()
