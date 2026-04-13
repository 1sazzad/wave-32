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
import unicodedata
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

# ── Signer configuration ──────────────────────────────────────────────────────
# Default signer values used if config file is missing or incomplete.
DEFAULT_PRESIDENT_NAME = "Md Sazzad Hossain"
DEFAULT_PRESIDENT_TITLE = "President, Programming Club of IST"
DEFAULT_DEPT_HEAD_NAME = "Prof. Dr. [Name]"
DEFAULT_DEPT_HEAD_TITLE = "Head, Dept. of CSE, IST"

# ── File paths ────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
CSV_PATH   = os.path.join(BASE_DIR, "responses.csv")
PCIST_LOGO = os.path.join(BASE_DIR, "pcist_logo.png")
IST_LOGO   = os.path.join(BASE_DIR, "ist_logo.png")
SIGN_PRES  = os.path.join(BASE_DIR, "signature_president.png")  # replace with real signature
SIGN_DH    = os.path.join(BASE_DIR, "signature_depthead.png")   # replace with real signature
OUTPUT_DIR = os.path.join(BASE_DIR, "certificates")
MANIFEST   = os.path.join(BASE_DIR, "cert_manifest.json")
SIGNER_CONFIG = os.path.join(BASE_DIR, "signer_config.json")


def load_signer_config(config_path):
    """Load signer names/titles from JSON config with safe defaults."""
    data = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
                if isinstance(raw, dict):
                    data = raw
        except Exception:
            data = {}

    return {
        "president_name": str(data.get("president_name", DEFAULT_PRESIDENT_NAME)).strip() or DEFAULT_PRESIDENT_NAME,
        "president_title": str(data.get("president_title", DEFAULT_PRESIDENT_TITLE)).strip() or DEFAULT_PRESIDENT_TITLE,
        "dept_head_name": str(data.get("dept_head_name", DEFAULT_DEPT_HEAD_NAME)).strip() or DEFAULT_DEPT_HEAD_NAME,
        "dept_head_title": str(data.get("dept_head_title", DEFAULT_DEPT_HEAD_TITLE)).strip() or DEFAULT_DEPT_HEAD_TITLE,
    }


_signers = load_signer_config(SIGNER_CONFIG)
PRESIDENT_NAME = sys.argv[1] if len(sys.argv) > 1 else _signers["president_name"]
PRESIDENT_TITLE = sys.argv[2] if len(sys.argv) > 2 else _signers["president_title"]
DEPT_HEAD_NAME = sys.argv[3] if len(sys.argv) > 3 else _signers["dept_head_name"]
DEPT_HEAD_TITLE = sys.argv[4] if len(sys.argv) > 4 else _signers["dept_head_title"]

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Color palette (minimal ICPC-style look) ──────────────────────────────────
WHITE      = colors.white
NAVY       = colors.HexColor("#102A43")
CHARCOAL   = colors.HexColor("#1F2933")
MID_GRAY   = colors.HexColor("#52606D")
LIGHT_GRAY = colors.HexColor("#D9E2EC")
GOLD       = colors.HexColor("#D4A574")
DARK_GOLD  = colors.HexColor("#B8860B")

W, H = landscape(A4)


def draw_certificate(cv, participant_name, team_name, index,
                     pres_name, pres_title, dh_name, dh_title):

    page_margin = 18 * mm

    # ── Background ─────────────────────────────────────────
    cv.setFillColor(WHITE)
    cv.rect(0, 0, W, H, fill=1, stroke=0)

    # Outer border (thin + elegant)
    cv.setStrokeColor(LIGHT_GRAY)
    cv.setLineWidth(1.2)
    cv.rect(page_margin, page_margin, W - 2 * page_margin, H - 2 * page_margin)

    # Inner border
    cv.setStrokeColor(NAVY)
    cv.setLineWidth(0.8)
    cv.rect(page_margin + 4, page_margin + 4, W - 2 * page_margin - 8, H - 2 * page_margin - 8)

    # ── Bottom wave (modern ICPC feel) ─────────────────────
    cv.setFillColor(NAVY)
    cv.roundRect(0, 0, W, 40 * mm, 0, fill=1, stroke=0)

    cv.setFillColor(GOLD)
    cv.roundRect(0, 0, W, 25 * mm, 0, fill=1, stroke=0)

    # ── Logos ──────────────────────────────────────────────
    logo_size = 20 * mm
    logo_y = H - page_margin - 20 * mm

    try:
        cv.drawImage(PCIST_LOGO, page_margin + 5 * mm, logo_y,
                     width=logo_size, height=logo_size, mask='auto')
    except:
        pass

    try:
        cv.drawImage(IST_LOGO, W - page_margin - 5 * mm - logo_size, logo_y,
                     width=logo_size, height=logo_size, mask='auto')
    except:
        pass

    # ── Header ─────────────────────────────────────────────
    cv.setFillColor(NAVY)
    cv.setFont("Helvetica-Bold", 13)
    cv.drawCentredString(W / 2, H - page_margin - 8 * mm,
                         "INSTITUTE OF SCIENCE AND TECHNOLOGY")

    cv.setFont("Helvetica", 10)
    cv.setFillColor(MID_GRAY)
    cv.drawCentredString(W / 2, H - page_margin - 14 * mm,
                         "Programming Club of IST (pcIST) · DHAKA, BANGLADESH")

    # ── Title ──────────────────────────────────────────────
    title_y = H - page_margin - 45 * mm

    cv.setFont("Times-Bold", 44)
    cv.setFillColor(NAVY)
    cv.drawCentredString(W / 2, title_y, "CERTIFICATE")

    cv.setFont("Helvetica", 12)
    cv.setFillColor(MID_GRAY)
    cv.drawCentredString(W / 2, title_y - 10 * mm, "OF PARTICIPATION")

    # Decorative line
    cv.setStrokeColor(GOLD)
    cv.setLineWidth(1.5)
    cv.line(W * 0.35, title_y - 13 * mm, W * 0.65, title_y - 13 * mm)

    # ── Recipient ──────────────────────────────────────────
    intro_y = title_y - 25 * mm

    cv.setFont("Helvetica-Oblique", 11)
    cv.setFillColor(MID_GRAY)
    cv.drawCentredString(W / 2, intro_y,
                         "This certificate is proudly presented to")

    # Name
    name_font = 32
    max_width = W * 0.7

    while cv.stringWidth(participant_name, "Times-Bold", name_font) > max_width and name_font > 18:
        name_font -= 1

    cv.setFont("Times-Bold", name_font)
    cv.setFillColor(NAVY)
    cv.drawCentredString(W / 2, intro_y - 12 * mm, participant_name)

    # Underline
    cv.setStrokeColor(GOLD)
    cv.setLineWidth(1)
    cv.line(W * 0.25, intro_y - 14 * mm, W * 0.75, intro_y - 14 * mm)

    # ── Event Info ─────────────────────────────────────────
    msg_y = intro_y - 25 * mm

    cv.setFont("Helvetica", 11)
    cv.setFillColor(MID_GRAY)
    cv.drawCentredString(W / 2, msg_y, "for outstanding participation in")

    cv.setFont("Helvetica-Bold", 16)
    cv.setFillColor(NAVY)
    cv.drawCentredString(W / 2, msg_y - 10 * mm, "RESTART-30")

    cv.setFont("Helvetica", 10)
    cv.setFillColor(MID_GRAY)
    cv.drawCentredString(W / 2, msg_y - 16 * mm, "Programming Contest · August 2025")
    cv.drawCentredString(W / 2, msg_y - 21 * mm, "Organized by Programming Club of IST (pcIST)")
    cv.drawCentredString(W / 2, msg_y - 26 * mm, f"Team: {team_name}")

    # ── Signature Section ──────────────────────────────────
    sign_y = page_margin + 30 * mm

    cv.setStrokeColor(LIGHT_GRAY)
    cv.setLineWidth(0.8)
    cv.line(W * 0.15, sign_y + 10 * mm, W * 0.85, sign_y + 10 * mm)

    sig_positions = [W * 0.3, W * 0.7]
    names = [pres_name, dh_name]
    titles = [pres_title, dh_title]
    images = [SIGN_PRES, SIGN_DH]

    for x, name, title, img in zip(sig_positions, names, titles, images):

        try:
            cv.drawImage(img, x - 15 * mm, sign_y + 2 * mm,
                         width=30 * mm, height=10 * mm, mask='auto')
        except:
            pass

        cv.setStrokeColor(CHARCOAL)
        cv.line(x - 30 * mm, sign_y, x + 30 * mm, sign_y)

        cv.setFont("Helvetica-Bold", 9)
        cv.setFillColor(NAVY)
        cv.drawCentredString(x, sign_y - 5 * mm, name)

        cv.setFont("Helvetica", 8)
        cv.setFillColor(MID_GRAY)
        cv.drawCentredString(x, sign_y - 9 * mm, title)

    # ── Certificate ID ─────────────────────────────────────
    cv.setFont("Helvetica", 8.5)
    cv.setFillColor(MID_GRAY)
    cv.drawCentredString(W / 2, page_margin + 5 * mm,
                         f"CERTIFICATE ID: PCIST / RESTART-30 / 2025 / {index:03d}")

def parse_participants(csv_path):
    """Parse all participants (leader + member 2 + member 3) from Google Form CSV export."""
    def normalize_header(value):
        return "".join(ch for ch in value.lower() if ch.isalnum())

    def clean_name(value):
        # Remove zero-width/invisible format chars and normalize spaces.
        cleaned = "".join(ch for ch in value if unicodedata.category(ch) != "Cf")
        return " ".join(cleaned.split())

    def find_column(header_map, aliases):
        for alias in aliases:
            key = normalize_header(alias)
            if key in header_map:
                return header_map[key]
        return None

    participants = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        header_map = {normalize_header(h): h for h in headers if h}

        team_col = find_column(header_map, ["Team Name"])
        member_cols = [
            (
                find_column(header_map, ["Team Leader Name", "Member -1", "Member 1"]),
                find_column(header_map, ["Team Leader Email", "Member -1 email", "Member 1 email"]),
            ),
            (
                find_column(header_map, ["Member 2 Name", "Member - 2", "Member -2", "Member 2"]),
                find_column(header_map, ["Member 2 Email", "Member - 2 email", "Member -2 email", "Member 2 email"]),
            ),
            (
                find_column(header_map, ["Member 3 Name", "Member - 3", "Member -3", "Member 3"]),
                find_column(header_map, ["Member 3 Email", "Member - 3 email", "Member -3 email", "Member 3 email"]),
            ),
        ]

        if not team_col:
            raise ValueError("Could not find 'Team Name' column in responses.csv")

        for row in reader:
            team = " ".join(row.get(team_col, "").split())
            for name_col, email_col in member_cols:
                if not name_col or not email_col:
                    continue

                name = clean_name(row.get(name_col, ""))
                email = "".join(row.get(email_col, "").split())
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
