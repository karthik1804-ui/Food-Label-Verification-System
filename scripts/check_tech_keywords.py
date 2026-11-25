import re

def check_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
    print(f"=== {filename} ===")
    
    # Check for technical accuracy words
    for kw in ['preference_engine.py', 'barcode.py', 'audit.py', 'React 18', 'React 19', 'FastAPI', 'Flask', 'PostgreSQL', 'SQLite']:
        c = text.count(kw)
        if c > 0:
            print(f"  Found '{kw}': {c} times")

for num in [3, 4, 5, 6, 7]:
    check_file(f"d:/food-risk-checker/scripts/report_chapters/chapter_{num}.py")
