import re

def print_fig_calls(num):
    fpath = f"d:/food-risk-checker/scripts/report_chapters/chapter_{num}.py"
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    print(f"=== Chapter {num} ===")
    matches = re.findall(r'builder\.add_figure\(\s*(".*?",\s*".*?",\s*width_inches=[\d\.]+)', content, re.DOTALL)
    for m in matches:
        print("  " + m.replace("\n", " "))

for n in [3, 4, 5, 6]:
    print_fig_calls(n)
