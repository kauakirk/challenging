"""
generate_pdf.py
---------------
Converte report/final_report.md para final_report.pdf na raiz do projeto.
Uso: python scripts/generate_pdf.py
"""

import re
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Preformatted
)
from reportlab.lib.enums import TA_LEFT

BASE    = Path(__file__).parent.parent
MD_PATH = BASE / "report" / "final_report.md"
PDF_PATH= BASE / "final_report.pdf"

# ---------------------------------------------------------------------------
# Estilos
# ---------------------------------------------------------------------------
styles = getSampleStyleSheet()

H1 = ParagraphStyle("H1", parent=styles["Heading1"],
    fontSize=18, textColor=colors.HexColor("#1a1a2e"),
    spaceAfter=8, spaceBefore=0)
H2 = ParagraphStyle("H2", parent=styles["Heading2"],
    fontSize=14, textColor=colors.HexColor("#16213e"),
    spaceAfter=6, spaceBefore=16,
    borderPadding=(0,0,2,0))
H3 = ParagraphStyle("H3", parent=styles["Heading3"],
    fontSize=11, textColor=colors.HexColor("#0f3460"),
    spaceAfter=4, spaceBefore=10)
BODY = ParagraphStyle("BODY", parent=styles["Normal"],
    fontSize=10, leading=15, spaceAfter=4)
BULLET = ParagraphStyle("BULLET", parent=BODY,
    leftIndent=20, bulletIndent=10, spaceAfter=2)
CODE = ParagraphStyle("CODE", parent=styles["Code"],
    fontSize=8, leading=11, backColor=colors.HexColor("#f0f0f0"),
    leftIndent=12, rightIndent=12)
QUOTE = ParagraphStyle("QUOTE", parent=BODY,
    leftIndent=16, textColor=colors.HexColor("#555555"),
    borderPadding=(4, 4, 4, 8))

# ---------------------------------------------------------------------------
# Parser Markdown → ReportLab flowables
# ---------------------------------------------------------------------------

def escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline_fmt(text: str) -> str:
    """Converte **bold**, `code` e links inline."""
    text = escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r'<font name="Courier" size="9" backColor="#f0f0f0">\1</font>', text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    return text


def parse_table(lines: list) -> Table | None:
    rows = []
    for line in lines:
        if re.match(r"^\s*\|[-:| ]+\|\s*$", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append(cells)
    if not rows:
        return None

    col_count = max(len(r) for r in rows)
    # Normaliza
    rows = [r + [""] * (col_count - len(r)) for r in rows]

    # Formata células
    formatted = []
    for i, row in enumerate(rows):
        fmt_row = []
        for cell in row:
            style = BODY if i > 0 else ParagraphStyle(
                "TH", parent=BODY, textColor=colors.white, fontName="Helvetica-Bold")
            fmt_row.append(Paragraph(inline_fmt(cell), style))
        formatted.append(fmt_row)

    col_width = (A4[0] - 4*cm) / col_count
    t = Table(formatted, colWidths=[col_width]*col_count, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
        ("GRID",       (0,0), (-1,-1), 0.4, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f5f5f5")]),
        ("FONTSIZE",   (0,0), (-1,-1), 9),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",  (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("VALIGN",     (0,0), (-1,-1), "TOP"),
    ]))
    return t


def md_to_flowables(md: str) -> list:
    flowables = []
    lines = md.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i]

        # H1
        if line.startswith("# ") and not line.startswith("## "):
            flowables.append(Paragraph(inline_fmt(line[2:]), H1))
            flowables.append(HRFlowable(width="100%", thickness=1.5,
                color=colors.HexColor("#1a1a2e"), spaceAfter=6))
            i += 1; continue

        # H2
        if line.startswith("## "):
            flowables.append(Spacer(1, 6))
            flowables.append(Paragraph(inline_fmt(line[3:]), H2))
            flowables.append(HRFlowable(width="100%", thickness=0.5,
                color=colors.HexColor("#cccccc"), spaceAfter=4))
            i += 1; continue

        # H3
        if line.startswith("### "):
            flowables.append(Paragraph(inline_fmt(line[4:]), H3))
            i += 1; continue

        # Code block
        if line.startswith("```"):
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            flowables.append(Preformatted("\n".join(code_lines), CODE))
            i += 1; continue

        # Blockquote
        if line.startswith("> "):
            flowables.append(Paragraph(inline_fmt(line[2:]), QUOTE))
            i += 1; continue

        # Table
        if line.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].startswith("|"):
                table_lines.append(lines[i])
                i += 1
            t = parse_table(table_lines)
            if t:
                flowables.append(Spacer(1, 4))
                flowables.append(t)
                flowables.append(Spacer(1, 4))
            continue

        # Bullet
        if line.startswith("- ") or line.startswith("* "):
            flowables.append(Paragraph("• " + inline_fmt(line[2:]), BULLET))
            i += 1; continue

        # Numbered list
        if re.match(r"^\d+\. ", line):
            num, text = line.split(". ", 1)
            flowables.append(Paragraph(f"{num}. {inline_fmt(text)}", BULLET))
            i += 1; continue

        # HR
        if line.startswith("---"):
            flowables.append(HRFlowable(width="100%", thickness=0.5,
                color=colors.HexColor("#dddddd"), spaceBefore=4, spaceAfter=4))
            i += 1; continue

        # Empty line
        if not line.strip():
            flowables.append(Spacer(1, 4))
            i += 1; continue

        # Normal paragraph
        flowables.append(Paragraph(inline_fmt(line), BODY))
        i += 1

    return flowables


# ---------------------------------------------------------------------------
# Gera PDF
# ---------------------------------------------------------------------------
def main():
    md = MD_PATH.read_text(encoding="utf-8")
    flowables = md_to_flowables(md)

    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm,  bottomMargin=2*cm,
        title="MotoAssist — Relatório Final Desafio 2",
        author="kauakirk",
    )
    doc.build(flowables)
    print(f"PDF gerado: {PDF_PATH}")


if __name__ == "__main__":
    main()
