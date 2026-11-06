"""Strip main.tex to plain body text and run the articlecraft lint on it. Also lists sentences over 25 words.

    python 03_Advionics/submission/report_build/lint_report.py
"""
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
s = (HERE.parent / "latex" / "main.tex").read_text(encoding="utf-8")
b = s[s.index(r"\section{Introduction}"):s.index(r"\clearpage")]


def float_text(m):
    return "\n" + " ".join(re.findall(r"\\caption\{(.*?)\}\n", m.group(0))) + "\n"


b = re.sub(r"\\begin\{(figure|table|equation)\}.*?\\end\{\1\}", float_text, b, flags=re.S)
b = re.sub(r"\\(section|subsection)\{(.*?)\}", r"\n# \2\n", b)
b = re.sub(r"\\cite\{.*?\}|\\label\{.*?\}|~?\\ref\{.*?\}", "", b)
b = re.sub(r"\$[^$]*\$", "X", b)
b = re.sub(r"\\textbf\{(.*?)\}", r"\1", b)
b = b.replace("\\%", "%").replace("\\item", "-").replace("``", '"').replace("''", '"')
b = re.sub(r"\\begin\{itemize\}|\\end\{itemize\}", "", b)
out = HERE / "report_text.md"
out.write_text(b, encoding="utf-8")
print("words", len(b.split()))
for sent in re.split(r"(?<=[.?!])\s+", re.sub(r"\s+", " ", b)):
    n = len(sent.split())
    if n > 25:
        print(n, sent[:150])
lint = r"C:\Users\ayber\Desktop\Custom Yetenekler\articlecraft\scripts\article_lint.py"
r = subprocess.run([sys.executable, lint, str(out)], capture_output=True, text=True, encoding="utf-8")
print(r.stdout[:3000], r.stderr[:500])
