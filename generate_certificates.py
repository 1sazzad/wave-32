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

    # 1. Cream background
    cv.setFillColor(CREAM)
    cv.rect(0, 0, W, H, fill=1, stroke=0)

    # 2. Full-bleed top & bottom navy bars
    bar_h = 14 * mm
    cv.setFillColor(NAVY)
    cv.rect(0, H - bar_h, W, bar_h, fill=1, stroke=0)
    cv.rect(0, 0, W, bar_h, fill=1, stroke=0)
    cv.setStrokeColor(GOLD2); cv.setLineWidth(1.2)
    cv.line(0, H - bar_h - 1, W, H - bar_h - 1)
    cv.line(0, bar_h + 1, W, bar_h + 1)

    # 3. Outer border frame (double line)
    m = 6 * mm
    cv.setStrokeColor(GOLD1); cv.setLineWidth(2.5)
    cv.rect(m, m, W - 2*m, H - 2*m, fill=0, stroke=1)
    cv.setStrokeColor(GOLD3); cv.setLineWidth(0.6)
    cv.rect(m + 3, m + 3, W - 2*m - 6, H - 2*m - 6, fill=0, stroke=1)

    # 4. Corner flourishes
    def flourish(cx, cy, rot):
        cv.saveState()
        cv.translate(cx, cy); cv.rotate(rot)
        cv.setStrokeColor(GOLD1); cv.setLineWidth(1)
        cv.setFillColor(GOLD1)
        cv.line(0, 0, 18, 0); cv.line(0, 0, 0, 18)
        p = cv.beginPath()
        p.moveTo(0, 5); p.lineTo(5, 0); p.lineTo(0, -5); p.lineTo(-5, 0); p.close()
        cv.drawPath(p, fill=1, stroke=0)
        for d in [8, 14]:
            cv.line(d, -2, d, 2)
            cv.line(-2, d, 2, d)
        cv.restoreState()

    pad = m + 5
    flourish(pad,     H - pad,  0)
    flourish(W - pad, H - pad, -90)
    flourish(pad,     pad,      90)
    flourish(W - pad, pad,      180)

    # 5. Logos + institute name in top bar
    logo_sz = 10 * mm
    logo_y  = H - bar_h + (bar_h - logo_sz) / 2
    try:
        cv.drawImage(PCIST_LOGO, 16*mm, logo_y,
                     width=logo_sz, height=logo_sz, preserveAspectRatio=True, mask='auto')
    except Exception:
        pass
    try:
        cv.drawImage(IST_LOGO, W - 16*mm - logo_sz, logo_y,
                     width=logo_sz, height=logo_sz, preserveAspectRatio=True, mask='auto')
    except Exception:
        pass
    cv.setFillColor(WHITE); cv.setFont("Helvetica-Bold", 9)
    cv.drawCentredString(W/2, H - bar_h + bar_h * 0.58,
                         "INSTITUTE OF SCIENCE AND TECHNOLOGY")
    cv.setFont("Helvetica", 7); cv.setFillColor(GOLD3)
    cv.drawCentredString(W/2, H - bar_h + bar_h * 0.22,
                         "Programming Club of IST  \u00b7  Dhaka, Bangladesh")

    # 6. "CERTIFICATE OF PARTICIPATION" heading
    top_y = H - bar_h - 16*mm
    cv.setFillColor(NAVY); cv.setFont("Helvetica-Bold", 30)
    cv.drawCentredString(W/2, top_y, "CERTIFICATE")
    sub_y    = top_y - 8*mm
    sub_text = "OF  PARTICIPATION"
    sub_w    = cv.stringWidth(sub_text, "Helvetica", 11)
    cv.setFont("Helvetica", 11); cv.setFillColor(GOLD1)
    cv.drawCentredString(W/2, sub_y, sub_text)
    gap    = 8
    line_w = 52 * mm
    cv.setStrokeColor(GOLD2); cv.setLineWidth(0.8)
    cv.line(W/2 - sub_w/2 - gap - line_w, sub_y + 4, W/2 - sub_w/2 - gap, sub_y + 4)
    cv.line(W/2 + sub_w/2 + gap, sub_y + 4, W/2 + sub_w/2 + gap + line_w, sub_y + 4)

    # 7. Divider line
    div_y = sub_y - 6*mm
    cv.setStrokeColor(LIGHT_LINE); cv.setLineWidth(0.5)
    cv.line(W * 0.12, div_y, W * 0.88, div_y)

    # 8. "This is to certify that"
    cv.setFillColor(MID_GRAY); cv.setFont("Helvetica-Oblique", 10)
    cv.drawCentredString(W/2, div_y - 9*mm, "This is to certify that")

    # 9. Participant name with ivory highlight strip
    name_y       = div_y - 21*mm
    name_strip_h = 10*mm
    cv.setFillColor(IVORY)
    cv.rect(W * 0.15, name_y - 1*mm, W * 0.70, name_strip_h, fill=1, stroke=0)
    cv.setStrokeColor(GOLD2); cv.setLineWidth(0.7)
    cv.line(W * 0.15, name_y - 1*mm, W * 0.85, name_y - 1*mm)
    cv.line(W * 0.15, name_y - 1*mm + name_strip_h, W * 0.85, name_y - 1*mm + name_strip_h)
    font_size = 24
    while cv.stringWidth(participant_name, "Helvetica-Bold", font_size) > W * 0.60 and font_size > 14:
        font_size -= 1
    cv.setFillColor(NAVY); cv.setFont("Helvetica-Bold", font_size)
    cv.drawCentredString(W/2, name_y + 2*mm, participant_name)

    # 10. Team name
    cv.setFillColor(MID_GRAY); cv.setFont("Helvetica", 9.5)
    cv.drawCentredString(W/2, name_y - 7*mm, "representing team")
    cv.setFillColor(GOLD1); cv.setFont("Helvetica-Bold", 13)
    cv.drawCentredString(W/2, name_y - 14*mm, team_name)

    # 11. Contest name box
    cv.setFillColor(MID_GRAY); cv.setFont("Helvetica", 9.5)
    cv.drawCentredString(W/2, name_y - 21*mm, "has successfully participated in")
    cbox_y = name_y - 33*mm
    cbox_h = 12*mm
    cv.setFillColor(NAVY)
    cv.roundRect(W/2 - 52*mm, cbox_y, 104*mm, cbox_h, 2*mm, fill=1, stroke=0)
    cv.setFillColor(WHITE); cv.setFont("Helvetica-Bold", 13)
    cv.drawCentredString(W/2, cbox_y + cbox_h * 0.55, "ReSterT \u2014 30")
    cv.setFillColor(GOLD3); cv.setFont("Helvetica", 8)
    cv.drawCentredString(W/2, cbox_y + cbox_h * 0.18,
                         "Intra-University Programming Contest  \u00b7  August 2025")

    # 12. Divider above signature area
    sdiv_y = bar_h + 22*mm
    cv.setStrokeColor(LIGHT_LINE); cv.setLineWidth(0.5)
    cv.line(W * 0.12, sdiv_y, W * 0.88, sdiv_y)

    # 13. Signatures (image + line + name + title)
    sig_cx     = [W * 0.28, W * 0.72]
    sig_names  = [pres_name,  dh_name]
    sig_titles = [pres_title, dh_title]
    sig_imgs   = [SIGN_PRES,  SIGN_DH]

    for sx, sn, st, si in zip(sig_cx, sig_names, sig_titles, sig_imgs):
        sig_h  = 9 * mm
        sig_w  = 24 * mm
        sig_y  = sdiv_y - sig_h - 1*mm
        try:
            cv.drawImage(si, sx - sig_w/2, sig_y,
                         width=sig_w, height=sig_h,
                         preserveAspectRatio=True, mask='auto')
        except Exception:
            pass
        line_y = sig_y - 1*mm
        cv.setStrokeColor(CHARCOAL); cv.setLineWidth(0.6)
        cv.line(sx - 28*mm, line_y, sx + 28*mm, line_y)
        cv.setFillColor(NAVY); cv.setFont("Helvetica-Bold", 8.5)
        cv.drawCentredString(sx, line_y - 4.5*mm, sn)
        cv.setFillColor(MID_GRAY); cv.setFont("Helvetica", 7.5)
        cv.drawCentredString(sx, line_y - 8.5*mm, st)

    # 14. Certificate serial number in bottom bar
    cv.setFillColor(GOLD3); cv.setFont("Helvetica", 7)
    cv.drawCentredString(W/2, bar_h * 0.35,
                         f"PCIST / ReSterT-30 / 2025 / {index:03d}")


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
