import os
import re

ch_dir = r"d:\food-risk-checker\scripts\report_chapters"
for f in sorted(os.listdir(ch_dir)):
    if f.endswith('.py'):
        with open(os.path.join(ch_dir, f), 'r', encoding='utf-8') as fp:
            c = fp.read()
            imgs = re.findall(r'"(fig_[^"]+\.png)"', c)
            if imgs:
                print(f"{f}: {imgs}")
