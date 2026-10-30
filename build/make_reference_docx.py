"""Creates build/styles/reference.docx: pandoc's default reference document restyled
with the book palette (navy headings, coloured callout paragraph styles)."""
import subprocess
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Mm

HERE = Path(__file__).parent
OUT = HERE / "styles" / "reference.docx"

PALETTE = {
    "navy": "1B2A4A", "blue": "1F5FA8", "teal": "127A7A", "green": "3C7A4A",
    "amber": "B7791F", "grey": "8A94A6",
}
CALLOUTS = {
    "Callout Definition": ("blue", "EEF4FB"), "Callout Formula": ("blue", "EEF4FB"),
    "Callout Concept": ("teal", "ECF6F6"), "Callout Industry": ("teal", "ECF6F6"),
    "Callout Tip": ("green", "EEF5EF"), "Callout Recommendation": ("green", "EEF5EF"),
    "Callout Mistake": ("amber", "FBF4E6"), "Callout Warning": ("amber", "FBF4E6"),
    "Callout Example": ("grey", "F4F5F7"), "Callout Note": ("grey", "F4F5F7"),
    "Callout Summary": ("navy", "EEF4FB"),
}


def shade_and_border(style, border_hex, fill_hex):
    ppr = style.element.get_or_add_pPr()
    bdr = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    for k, v in {"w:val": "single", "w:sz": "24", "w:space": "8", "w:color": border_hex}.items():
        left.set(qn(k), v)
    bdr.append(left)
    ppr.append(bdr)
    shd = OxmlElement("w:shd")
    for k, v in {"w:val": "clear", "w:color": "auto", "w:fill": fill_hex}.items():
        shd.set(qn(k), v)
    ppr.append(shd)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["pandoc", "-o", str(OUT), "--print-default-data-file", "reference.docx"], check=True)
    doc = Document(str(OUT))
    for section in doc.sections:
        section.left_margin = section.right_margin = Mm(22)
        section.top_margin = section.bottom_margin = Mm(22)

    styles = doc.styles
    by_name = {s.name: s for s in styles}
    for name in ("Normal", "Body Text", "First Paragraph", "Compact"):
        if name in by_name:
            f = by_name[name].font
            f.name = "Georgia"
            f.size = Pt(10.5)
    for level, size in ((1, 22), (2, 15), (3, 12.5), (4, 11)):
        st = by_name[f"Heading {level}"]
        st.font.name = "Inter"
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = RGBColor.from_string(PALETTE["blue"] if level == 4 else PALETTE["navy"])
    if "Source Code" in by_name:
        by_name["Source Code"].font.size = Pt(8.5)

    for name, (color, fill) in CALLOUTS.items():
        st = styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        st.base_style = by_name["Normal"]
        st.font.size = Pt(10)
        st.paragraph_format.left_indent = Mm(3)
        st.paragraph_format.space_after = Pt(3)
        shade_and_border(st, PALETTE[color], fill)
    doc.save(str(OUT))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
