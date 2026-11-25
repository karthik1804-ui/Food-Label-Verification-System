import re
import os
import docx

def audit_report():
    ch7_path = r"d:\food-risk-checker\scripts\report_chapters\chapter_7.py"
    with open(ch7_path, "r", encoding="utf-8") as f:
        ch7_content = f.read()

    # Find all references
    refs = re.findall(r'builder\.add_p\("(\[\d+\].*?)"\)', ch7_content, re.DOTALL)
    print(f"Total references parsed: {len(refs)}")
    for i, r in enumerate(refs):
        print(f"Ref {i+1}: {r}")

if __name__ == "__main__":
    audit_report()
