"""
ReSterT-30 Certificate Generator
=================================
Generates ICPC-style participation certificates for all contest participants.

Usage:
    python generate_certificates.py
    python generate_certificates.py "President Name" "President Title" "DeptHead Name" "DeptHead Title"

Requirements:
    pip install reportlab pillow

Output:
    certificates/NNN_Participant_Name.pdf  — one PDF per participant
    cert_manifest.json                     — participant list with PDF paths (used by email sender)
"""

import csv
import json
import os
import sys
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

# ── Signer configuration ──────────────────────────────────────────────────────
# Pass as command-line args, or edit the defaults here directly.
PRESIDENT_NAME  = sys.argv[1] if len(sys.argv) > 1 else "Md. Sazzad Hossain Arif"
PRESIDENT_TITLE = sys.argv[2] if len(sys.argv) > 2 else "President, Programming Club of IST"
DEPT_HEAD_NAME  = sys.argv[3] if len(sys.argv) > 3 else "Prof. Dr. [Name]"
DEPT_HEAD_TITLE = sys.argv[4] if len(sys.argv) > 4 else "Head, Dept. of CSE, IST"

# ── File paths ────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
CSV_PATH   = os.path.join(BASE_DIR, "responses.csv")
PCIST_LOGO = os.path.join(BASE_DIR, "pcist_logo.png")
IST_LOGO   = os.path.join(BASE_DIR, "ist_logo.png")
SIGN_PRES  = os.path.join(BASE_DIR, "signature_president.png")  # replace with real signature
SIGN_DH    = os.path.join(BASE_DIR, "signature_depthead.png")   # replace with real signature
OUTPUT_DIR = os.path.join(BASE_DIR, "certificates")
MANIFEST   = os.path.join(BASE_DIR, "cert_manifest.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Color palette ─────────────────────────────────────────────────────────────
CREAM      = colors.HexColor("#FEFCF5")
IVORY      = colors.HexColor("#F7F2E4")
GOLD1      = colors.HexColor("#B8860B")
GOLD2      = colors.HexColor("#D4A017")
GOLD3      = colors.HexColor("#F0D060")
NAVY       = colors.HexColor("#0A1628")
CHARCOAL   = colors.HexColor("#2C2C2C")
MID_GRAY   = colors.HexColor("#666666")
LIGHT_LINE = colors.HexColor("#D4BC7A")
WHITE      = colors.white

W, H = landscape(A4)


def draw_certificate(cv, participant_name, team_name, index,
                     pres_name, pres_title, dh_name, dh_title):
    page_margin = 10 * mm

    # Base paper and framing.
    cv.setFillColor(CREAM)
    cv.rect(0, 0, W, H, fill=1, stroke=0)

    cv.setStrokeColor(colors.HexColor("#C9A24D"))
    cv.setLineWidth(2.2)
    cv.rect(page_margin, page_margin, W - 2 * page_margin, H - 2 * page_margin, fill=0, stroke=1)

    inner_gap = 3.5
    cv.setStrokeColor(colors.HexColor("#E4C676"))
    cv.setLineWidth(0.8)
    cv.rect(
        page_margin + inner_gap,
        page_margin + inner_gap,
        W - 2 * (page_margin + inner_gap),
        H - 2 * (page_margin + inner_gap),
        fill=0,
        stroke=1,
    )

    # Visual identity bands.
    top_band_h = 24 * mm
    bottom_band_h = 16 * mm
    cv.setFillColor(NAVY)
    cv.rect(page_margin, H - page_margin - top_band_h, W - 2 * page_margin, top_band_h, fill=1, stroke=0)
    cv.setFillColor(colors.HexColor("#122742"))
    cv.rect(page_margin, page_margin, W - 2 * page_margin, bottom_band_h, fill=1, stroke=0)

    accent_h = 2.2 * mm
    cv.setFillColor(GOLD2)
    cv.rect(page_margin, H - page_margin - top_band_h - accent_h, W - 2 * page_margin, accent_h, fill=1, stroke=0)
    cv.rect(page_margin, page_margin + bottom_band_h, W - 2 * page_margin, accent_h, fill=1, stroke=0)

    # Logos and organizer lines.
    logo_size = 14 * mm
    logo_y = H - page_margin - top_band_h + (top_band_h - logo_size) / 2
    try:
        cv.drawImage(
            PCIST_LOGO,
            page_margin + 8 * mm,
            logo_y,
            width=logo_size,
            height=logo_size,
            preserveAspectRatio=True,
            mask='auto',
        )
    except Exception:
        pass
    try:
        cv.drawImage(
            IST_LOGO,
            W - page_margin - 8 * mm - logo_size,
            logo_y,
            width=logo_size,
            height=logo_size,
            preserveAspectRatio=True,
            mask='auto',
        )
    except Exception:
        pass

    cv.setFillColor(WHITE)
    cv.setFont("Helvetica-Bold", 10)
    cv.drawCentredString(W / 2, H - page_margin - 8.8 * mm, "INSTITUTE OF SCIENCE AND TECHNOLOGY")
    cv.setFont("Helvetica", 8)
    cv.setFillColor(colors.HexColor("#E9CC84"))
    cv.drawCentredString(W / 2, H - page_margin - 14.3 * mm, "PROGRAMMING CLUB OF IST · DHAKA, BANGLADESH")

    # Main title block.
    title_y = H - page_margin - top_band_h - 18 * mm
    cv.setFillColor(NAVY)
    cv.setFont("Times-Bold", 33)
    cv.drawCentredString(W / 2, title_y, "CERTIFICATE")

    subtitle = "OF PARTICIPATION"
    cv.setFont("Helvetica-Bold", 11)
    cv.setFillColor(colors.HexColor("#9D7730"))
    cv.drawCentredString(W / 2, title_y - 7 * mm, subtitle)

    sub_w = cv.stringWidth(subtitle, "Helvetica-Bold", 11)
    cv.setStrokeColor(colors.HexColor("#CBA552"))
    cv.setLineWidth(1)
    wing = 40 * mm
    wing_gap = 7
    wing_y = title_y - 4.8 * mm
    cv.line(W / 2 - sub_w / 2 - wing_gap - wing, wing_y, W / 2 - sub_w / 2 - wing_gap, wing_y)
    cv.line(W / 2 + sub_w / 2 + wing_gap, wing_y, W / 2 + sub_w / 2 + wing_gap + wing, wing_y)

    # Recipient section.
    intro_y = title_y - 18 * mm
    cv.setFillColor(MID_GRAY)
    cv.setFont("Helvetica-Oblique", 11)
    cv.drawCentredString(W / 2, intro_y, "This certificate is proudly presented to")

    name_box_w = W * 0.72
    name_box_h = 15 * mm
    name_box_x = (W - name_box_w) / 2
    name_box_y = intro_y - 14.5 * mm
    cv.setFillColor(IVORY)
    cv.roundRect(name_box_x, name_box_y, name_box_w, name_box_h, 3.2 * mm, fill=1, stroke=0)
    cv.setStrokeColor(colors.HexColor("#D9B970"))
    cv.setLineWidth(1)
    cv.roundRect(name_box_x, name_box_y, name_box_w, name_box_h, 3.2 * mm, fill=0, stroke=1)

    name_font = 27
    while cv.stringWidth(participant_name, "Times-Bold", name_font) > name_box_w - 14 * mm and name_font > 16:
        name_font -= 1
    cv.setFillColor(NAVY)
    cv.setFont("Times-Bold", name_font)
    cv.drawCentredString(W / 2, name_box_y + 4.5 * mm, participant_name)

    # Event detail cards.
    msg_y = name_box_y - 10 * mm
    cv.setFillColor(MID_GRAY)
    cv.setFont("Helvetica", 10)
    cv.drawCentredString(W / 2, msg_y, "for outstanding participation in")

    event_box_w = 122 * mm
    event_box_h = 14 * mm
    event_box_x = (W - event_box_w) / 2
    event_box_y = msg_y - 11.5 * mm
    cv.setFillColor(NAVY)
    cv.roundRect(event_box_x, event_box_y, event_box_w, event_box_h, 2.8 * mm, fill=1, stroke=0)
    cv.setFillColor(WHITE)
    cv.setFont("Helvetica-Bold", 14)
    cv.drawCentredString(W / 2, event_box_y + 8.2 * mm, "ReSterT - 30")
    cv.setFillColor(colors.HexColor("#E8C56A"))
    cv.setFont("Helvetica", 8.5)
    cv.drawCentredString(W / 2, event_box_y + 3.2 * mm, "Intra-University Programming Contest · August 2025")

    cv.setFillColor(MID_GRAY)
    cv.setFont("Helvetica", 9.5)
    cv.drawCentredString(W / 2, event_box_y - 6.5 * mm, "Representing Team")
    cv.setFillColor(colors.HexColor("#8A5B00"))
    cv.setFont("Helvetica-Bold", 13)
    cv.drawCentredString(W / 2, event_box_y - 12.2 * mm, team_name)

    # Signature strip.
    sign_line_y = page_margin + bottom_band_h + accent_h + 11 * mm
    cv.setStrokeColor(colors.HexColor("#D4B570"))
    cv.setLineWidth(0.7)
    cv.line(W * 0.12, sign_line_y + 9 * mm, W * 0.88, sign_line_y + 9 * mm)

    sig_centers = [W * 0.30, W * 0.70]
    sig_names = [pres_name, dh_name]
    sig_titles = [pres_title, dh_title]
    sig_images = [SIGN_PRES, SIGN_DH]

    for sx, signer_name, signer_title, signer_image in zip(sig_centers, sig_names, sig_titles, sig_images):
        sig_w = 28 * mm
        sig_h = 10 * mm
        sig_y = sign_line_y + 1.8 * mm
        try:
            cv.drawImage(
                signer_image,
                sx - sig_w / 2,
                sig_y,
                width=sig_w,
                height=sig_h,
                preserveAspectRatio=True,
                mask='auto',
            )
        except Exception:
            pass

        cv.setStrokeColor(CHARCOAL)
        cv.setLineWidth(0.7)
        cv.line(sx - 32 * mm, sign_line_y, sx + 32 * mm, sign_line_y)

        cv.setFillColor(NAVY)
        cv.setFont("Helvetica-Bold", 9)
        cv.drawCentredString(sx, sign_line_y - 4.2 * mm, signer_name)
        cv.setFillColor(MID_GRAY)
        cv.setFont("Helvetica", 7.8)
        cv.drawCentredString(sx, sign_line_y - 8.5 * mm, signer_title)

    # Serial number and note.
    cv.setFillColor(colors.HexColor("#E8C56A"))
    cv.setFont("Helvetica-Bold", 8)
    cv.drawCentredString(W / 2, page_margin + 5.5 * mm, f"CERTIFICATE ID: PCIST / ReSterT-30 / 2025 / {index:03d}")


def parse_participants(csv_path):
    """Parse all participants (leader + member 2 + member 3) from Google Form CSV export."""
    participants = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        for row in reader:
            team_col = [k for k in headers if 'Team Name' in k][0]
            team = row[team_col].strip()
            for name_col, email_col in [
                ("Team Leader Name   ", "Team Leader Email  "),
                (" Member 2 Name  ",    "Member 2 Email"),
                (" Member 3 Name  ",    "Member 3 Email"),
            ]:
                name  = row.get(name_col, "").strip()
                email = row.get(email_col, "").strip()
                if name and email and "@" in email:
                    participants.append({"name": name, "team": team, "email": email})
    return participants


def main():
    participants = parse_participants(CSV_PATH)
    print(f"Found {len(participants)} participants.\n")

    generated = []
    for i, p in enumerate(participants, 1):
        safe = "".join(ch for ch in p["name"]
                       if ch.isalnum() or ch in " _-").strip().replace(" ", "_")
        out_path = os.path.join(OUTPUT_DIR, f"{i:03d}_{safe}.pdf")

        cv = canvas.Canvas(out_path, pagesize=landscape(A4))
        draw_certificate(cv, p["name"], p["team"], i,
                         PRESIDENT_NAME, PRESIDENT_TITLE,
                         DEPT_HEAD_NAME, DEPT_HEAD_TITLE)
        cv.save()

        generated.append({**p, "pdf": out_path, "index": i})
        print(f"  [{i:02d}] {p['name']}  |  {p['team']}")

    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(generated, f, indent=2, ensure_ascii=False)

    print(f"\n✓ {len(generated)} certificates → {OUTPUT_DIR}/")
    print(f"✓ Manifest → {MANIFEST}")


if __name__ == "__main__":
    main()
