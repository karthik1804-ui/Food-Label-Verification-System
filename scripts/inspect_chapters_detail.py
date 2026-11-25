import os
import re

ch_dir = r"d:\food-risk-checker\scripts\report_chapters"

for f in sorted(os.listdir(ch_dir)):
    if f.endswith('.py') and f.startswith(('chapter_', 'part_a')):
        p = os.path.join(ch_dir, f)
        with open(p, 'r', encoding='utf-8') as fp:
            content = fp.read()
        
        # Extract headers and paragraph counts
        h1s = re.findall(r'builder\.add_h1\("([^"]+)"\)', content)
        h2s = re.findall(r'builder\.add_h2\("([^"]+)"\)', content)
        ps = re.findall(r'builder\.add_p\(\s*"([^"]+)"', content)
        print(f"=== {f} ===")
        print(f"  H1 count: {len(h1s)}, H2 count: {len(h2s)}, Paragraph calls: {len(ps)}")
        print(f"  Sample H1s: {h1s[:3]}")
