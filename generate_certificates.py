"""Generate participant certificates from an HTML template and export as PDFs."""

import csv
import json
import os
import sys
import unicodedata

from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa

# Default signer values used if config file is missing or incomplete.
DEFAULT_PRESIDENT_NAME = "Md Sazzad Hossain"
DEFAULT_PRESIDENT_TITLE = "President, Programming Club of IST"
DEFAULT_DEPT_HEAD_NAME = "Prof. Dr. [Name]"
DEFAULT_DEPT_HEAD_TITLE = "Head, Dept. of CSE, IST"

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "responses.csv")
TEMPLATE_PATH = os.path.join(BASE_DIR, "certificate_template.html")
OUTPUT_DIR = os.path.join(BASE_DIR, "certificates")
MANIFEST = os.path.join(BASE_DIR, "cert_manifest.json")
SIGNER_CONFIG = os.path.join(BASE_DIR, "signer_config.json")

# Assets used by the HTML template
BACKGROUND_IMAGE = "certificate_design.png"
LEFT_LOGO = "pcist_logo.png"
RIGHT_LOGO = "ist_logo.png"
PRES_SIGNATURE = "signature_president.png"
DH_SIGNATURE = "signature_depthead.png"

# Contest/template text
ORG_HEADER = "INSTITUTE OF SCIENCE AND TECHNOLOGY"
ORG_SUBHEADER = "Programming Club of IST (pcIST) · DHAKA, BANGLADESH"
CERTIFICATE_TITLE = "CERTIFICATE"
CERTIFICATE_SUBTITLE = "OF PARTICIPATION"
PRESENTED_LINE = "This certificate is proudly presented to"
PARTICIPATION_LINE = "for outstanding participation in"
CONTEST_NAME = "RESTART-30"
CONTEST_DATE = "August 2025"
DETAIL_LINE_2 = "Organized by Programming Club of IST (pcIST)"


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


def link_callback(uri, rel):
    """Resolve local asset paths for xhtml2pdf."""
    if os.path.isabs(uri):
        return uri
    return os.path.join(BASE_DIR, uri)


def render_pdf_from_template(template, context, output_path):
    html = template.render(**context)
    with open(output_path, "wb") as pdf_file:
        result = pisa.CreatePDF(
            src=html,
            dest=pdf_file,
            encoding="utf-8",
            link_callback=link_callback,
        )
    if result.err:
        raise RuntimeError(f"Failed to generate PDF: {output_path}")


def parse_participants(csv_path):
    """Parse all participants (leader + member 2 + member 3) from CSV export."""

    def normalize_header(value):
        return "".join(ch for ch in value.lower() if ch.isalnum())

    def clean_name(value):
        cleaned = "".join(ch for ch in value if unicodedata.category(ch) != "Cf")
        return " ".join(cleaned.split())

    def find_column(header_map, aliases):
        for alias in aliases:
            key = normalize_header(alias)
            if key in header_map:
                return header_map[key]
        return None

    participants = []
    with open(csv_path, newline="", encoding="utf-8") as f:
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


def build_context(participant, index, president_name, president_title, dept_head_name, dept_head_title):
    return {
        "background_image": BACKGROUND_IMAGE,
        "left_logo": LEFT_LOGO,
        "right_logo": RIGHT_LOGO,
        "org_header": ORG_HEADER,
        "org_subheader": ORG_SUBHEADER,
        "certificate_title": CERTIFICATE_TITLE,
        "certificate_subtitle": CERTIFICATE_SUBTITLE,
        "presented_line": PRESENTED_LINE,
        "participant_name": participant["name"],
        "participation_line": PARTICIPATION_LINE,
        "contest_name": CONTEST_NAME,
        "detail_line_1": f"Programming Contest · {CONTEST_DATE}",
        "detail_line_2": DETAIL_LINE_2,
        "team_line": f"Team: {participant['team']}",
        "president_signature": PRES_SIGNATURE,
        "president_name": president_name,
        "president_title": president_title,
        "dept_head_signature": DH_SIGNATURE,
        "dept_head_name": dept_head_name,
        "dept_head_title": dept_head_title,
        "certificate_id": f"PCIST / RESTART-30 / 2025 / {index:03d}",
    }


def main():
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError("certificate_template.html not found")

    signers = load_signer_config(SIGNER_CONFIG)
    president_name = sys.argv[1] if len(sys.argv) > 1 else signers["president_name"]
    president_title = sys.argv[2] if len(sys.argv) > 2 else signers["president_title"]
    dept_head_name = sys.argv[3] if len(sys.argv) > 3 else signers["dept_head_name"]
    dept_head_title = sys.argv[4] if len(sys.argv) > 4 else signers["dept_head_title"]

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    env = Environment(loader=FileSystemLoader(BASE_DIR), autoescape=True)
    template = env.get_template("certificate_template.html")

    participants = parse_participants(CSV_PATH)
    print(f"Found {len(participants)} participants.\n")

    generated = []
    for i, participant in enumerate(participants, 1):
        safe_name = "".join(ch for ch in participant["name"] if ch.isalnum() or ch in " _-").strip().replace(" ", "_")
        out_path = os.path.join(OUTPUT_DIR, f"{i:03d}_{safe_name}.pdf")

        context = build_context(
            participant,
            i,
            president_name,
            president_title,
            dept_head_name,
            dept_head_title,
        )
        render_pdf_from_template(template, context, out_path)

        generated.append({**participant, "pdf": out_path, "index": i})
        print(f"  [{i:02d}] {participant['name']}  |  {participant['team']}")

    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(generated, f, indent=2, ensure_ascii=False)

    print(f"\nGenerated {len(generated)} certificates -> {OUTPUT_DIR}")
    print(f"Manifest -> {MANIFEST}")


if __name__ == "__main__":
    main()
