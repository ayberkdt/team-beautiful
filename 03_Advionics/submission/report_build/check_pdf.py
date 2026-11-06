"""Page count, fill of each page and a contact sheet of the report PDF.

    python 03_Advionics/submission/report_build/check_pdf.py <sheet.png>
"""
import sys
from pathlib import Path

import fitz
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
pdf = Path(__file__).resolve().parents[1] / "latex" / "main.pdf"
d = fitz.open(pdf)
print("pages", len(d))
for i, p in enumerate(d):
    b = [x for x in p.get_text("blocks") if 95 < x[1] < 745]
    print(i + 1, round(max(x[3] for x in b)) if b else 0, p.get_text()[:70].replace("\n", " | "))
if len(sys.argv) > 1:
    ims = []
    for i in range(len(d)):
        pm = d[i].get_pixmap(dpi=60)
        ims.append(Image.frombytes("RGB", (pm.width, pm.height), pm.samples))
    n = (len(ims) + 1) // 2
    s = Image.new("RGB", (n * ims[0].width, 2 * ims[0].height), "white")
    for k, im in enumerate(ims):
        s.paste(im, ((k % n) * im.width, (k // n) * im.height))
    s.save(sys.argv[1])
