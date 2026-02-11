from io import BytesIO
from decimal import Decimal
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os


# ── Register Turkish-compatible fonts ──
_FONT_DIR = "/usr/share/fonts/truetype/dejavu"
_FONTS_REGISTERED = False


def _register_fonts():
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return

    font_paths = {
        "DejaVuSans": os.path.join(_FONT_DIR, "DejaVuSans.ttf"),
        "DejaVuSans-Bold": os.path.join(_FONT_DIR, "DejaVuSans-Bold.ttf"),
    }

    for name, path in font_paths.items():
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont(name, path))
        else:
            # Fallback: try to find any dejavu font
            for search_dir in ["/usr/share/fonts", "/usr/local/share/fonts"]:
                for root, dirs, files in os.walk(search_dir):
                    for f in files:
                        if f == name.replace("-", "") + ".ttf" or f == name + ".ttf":
                            pdfmetrics.registerFont(TTFont(name, os.path.join(root, f)))
                            break

    _FONTS_REGISTERED = True


# ── Colors ──
PRIMARY = HexColor("#1a56db")
DARK = HexColor("#1f2937")
GRAY = HexColor("#6b7280")
LIGHT_BG = HexColor("#f9fafb")
BORDER = HexColor("#e5e7eb")
WHITE = HexColor("#ffffff")

# ── Font names (Turkish-safe) ──
FONT = "DejaVuSans"
FONT_BOLD = "DejaVuSans-Bold"


def generate_invoice_pdf(work_order, invoice, company_info: dict = None) -> BytesIO:
    """Generate a professional PDF invoice with Turkish character support."""
    _register_fonts()

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=15 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    elements = []

    # Custom styles with Turkish-safe font
    title_style = ParagraphStyle(
        "InvoiceTitle", parent=styles["Title"],
        fontSize=22, textColor=PRIMARY, spaceAfter=2 * mm,
        fontName=FONT_BOLD,
    )
    header_style = ParagraphStyle(
        "Header", parent=styles["Normal"],
        fontSize=10, textColor=DARK, fontName=FONT_BOLD,
    )
    normal_style = ParagraphStyle(
        "NormalText", parent=styles["Normal"],
        fontSize=9, textColor=DARK, leading=14, fontName=FONT,
    )
    small_style = ParagraphStyle(
        "SmallText", parent=styles["Normal"],
        fontSize=8, textColor=GRAY, leading=12, fontName=FONT,
    )

    info = company_info or {
        "name": "OtoServis Pro",
        "address": "Servis Adresi",
        "phone": "0212 000 00 00",
        "tax_office": "Vergi Dairesi",
        "tax_number": "1234567890",
    }

    # ── Header ──
    right_title = ParagraphStyle(
        "Right", parent=title_style, alignment=TA_RIGHT, fontSize=16
    )
    header_data = [
        [
            Paragraph(f"<b>{info['name']}</b>", title_style),
            Paragraph(
                f"<b>FATURA</b><br/><font size=9>{invoice.invoice_number}</font>",
                right_title,
            ),
        ],
        [
            Paragraph(
                f"{info['address']}<br/>Tel: {info['phone']}<br/>VD: {info['tax_office']} / {info['tax_number']}",
                small_style,
            ),
            Paragraph(
                f"<b>Tarih:</b> {invoice.issue_date.strftime('%d.%m.%Y')}<br/><b>İş Emri:</b> {work_order.work_order_number}",
                ParagraphStyle("RightSmall", parent=small_style, alignment=TA_RIGHT),
            ),
        ],
    ]
    header_table = Table(header_data, colWidths=[doc.width * 0.55, doc.width * 0.45])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 8 * mm))

    # ── Customer & Vehicle Info ──
    customer = work_order.customer
    vehicle = work_order.vehicle

    info_data = [
        [
            Paragraph("<b>MÜŞTERİ BİLGİLERİ</b>", header_style),
            Paragraph("<b>ARAÇ BİLGİLERİ</b>", header_style),
        ],
        [
            Paragraph(
                f"{customer.full_name}<br/>Tel: {customer.phone}<br/>{customer.address or ''}<br/>"
                f"{f'VKN: {customer.tax_number}' if customer.tax_number else ''}",
                normal_style,
            ),
            Paragraph(
                f"Plaka: <b>{vehicle.plate_number}</b><br/>"
                f"{vehicle.brand} {vehicle.model} ({vehicle.year or '-'})<br/>"
                f"KM: {work_order.km_in or '-'}",
                normal_style,
            ),
        ],
    ]
    info_table = Table(info_data, colWidths=[doc.width * 0.5, doc.width * 0.5])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_BG),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 10),
        ("TOPPADDING", (0, 1), (-1, 1), 6),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, BORDER),
        ("LINEBETWEEN", (0, 0), (-1, -1), 0.5, BORDER),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 6 * mm))

    # ── Items Table ──
    items_header = ["#", "Açıklama", "Tür", "Miktar", "Birim Fiyat", "İskonto", "Toplam"]
    items_data = [items_header]

    for idx, item in enumerate(work_order.items, 1):
        items_data.append([
            str(idx),
            item.description,
            "Parça" if item.type.value == "part" else "İşçilik",
            f"{item.quantity:.0f}",
            f"₺{item.unit_price:,.2f}",
            f"₺{item.discount:,.2f}",
            f"₺{item.total_price:,.2f}",
        ])

    col_widths = [doc.width * w for w in [0.05, 0.32, 0.1, 0.1, 0.14, 0.14, 0.15]]
    items_table = Table(items_data, colWidths=col_widths, repeatRows=1)
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
        ("FONTNAME", (0, 1), (-1, -1), FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (3, 0), (-1, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
        ("TOPPADDING", (0, 1), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
        ("LINEBELOW", (0, 0), (-1, -2), 0.25, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 6 * mm))

    # ── Totals ──
    totals_data = [
        ["Ara Toplam:", f"₺{work_order.subtotal:,.2f}"],
        ["İskonto Toplam:", f"-₺{work_order.discount_total:,.2f}"],
        [f"KDV (%{work_order.vat_rate:.0f}):", f"₺{work_order.vat_total:,.2f}"],
        ["GENEL TOPLAM:", f"₺{work_order.grand_total:,.2f}"],
    ]
    totals_table = Table(totals_data, colWidths=[doc.width * 0.3, doc.width * 0.2], hAlign="RIGHT")
    totals_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (0, -1), "RIGHT"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (-1, -2), FONT),
        ("FONTNAME", (0, -1), (-1, -1), FONT_BOLD),
        ("BACKGROUND", (0, -1), (-1, -1), PRIMARY),
        ("TEXTCOLOR", (0, -1), (-1, -1), WHITE),
        ("TOPPADDING", (0, -1), (-1, -1), 8),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, -2), 0.25, BORDER),
        ("BOTTOMPADDING", (0, 0), (-1, -2), 4),
        ("TOPPADDING", (0, 0), (-1, -2), 4),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 15 * mm))

    # ── Signature ──
    sig_normal = ParagraphStyle("Sig", parent=normal_style, alignment=TA_CENTER)
    sig_small = ParagraphStyle("SigSmall", parent=small_style, alignment=TA_CENTER)
    sig_data = [
        [
            Paragraph("<b>Teslim Eden</b>", sig_normal),
            Paragraph("<b>Teslim Alan</b>", sig_normal),
        ],
        ["", ""],
        [
            Paragraph("İmza / Kaşe", sig_small),
            Paragraph("İmza / Kaşe", sig_small),
        ],
    ]
    sig_table = Table(sig_data, colWidths=[doc.width * 0.4, doc.width * 0.4], rowHeights=[20, 50, 20])
    sig_table.setStyle(TableStyle([
        ("LINEBELOW", (0, 1), (0, 1), 0.5, DARK),
        ("LINEBELOW", (1, 1), (1, 1), 0.5, DARK),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
    ]))
    sig_table.hAlign = "CENTER"
    elements.append(sig_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer
