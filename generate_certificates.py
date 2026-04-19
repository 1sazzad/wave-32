"""Generate participant certificates from an HTML template and export as PDFs.

Supports two data sources:
1) responses.csv (Google Form export)
2) cert_manifest.json (existing participant list)
"""

import argparse
import csv
import json
import os
import tempfile
import unicodedata
from pathlib import Path
from typing import Dict, List

from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

# Default signer values used if config file is missing or incomplete.
DEFAULT_PRESIDENT_NAME = "Md Sazzad Hossain"
DEFAULT_PRESIDENT_TITLE = "President, Programming Club of IST"
DEFAULT_DEPT_HEAD_NAME = "Prof. Dr. [Name]"
DEFAULT_DEPT_HEAD_TITLE = "Head, Dept. of CSE, IST"

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV_PATH = os.path.join(BASE_DIR, "responses.csv")
DEFAULT_JSON_PATH = os.path.join(BASE_DIR, "cert_manifest.json")
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

# Contest/template text (dynamic config for all certificates)
TEMPLATE_TEXT = {
    "org_header": "INSTITUTE OF SCIENCE AND TECHNOLOGY",
    "org_subheader": "Programming Club of IST (pcIST) Â· DHAKA, BANGLADESH",
    "certificate_title": "CERTIFICATE",
    "certificate_subtitle": "OF PARTICIPATION",
    "presented_line": "This certificate is proudly presented to",
    "participation_line": "for outstanding participation in",
    "contest_name": "WAVE-32",
    "contest_date": "January 2026",
    "detail_line_2": "Organized by Programming Club of IST (pcIST)",
    "certificate_id_prefix": "PCIST / WAVE-32 / 2025",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Generate certificate PDFs from HTML template.")
    parser.add_argument("--source", choices=["csv", "json"], default="json", help="Participant source type.")
    parser.add_argument("--input", dest="input_path", default=None, help="Input file path. Defaults to responses.csv or cert_manifest.json.")
    parser.add_argument("--output-dir", default=OUTPUT_DIR, help="Output directory for certificate PDFs.")
    parser.add_argument("--template", default=TEMPLATE_PATH, help="HTML template path.")
    parser.add_argument("--manifest", default=MANIFEST, help="Output manifest JSON path.")
    parser.add_argument("--president-name", default=None)
    parser.add_argument("--president-title", default=None)
    parser.add_argument("--dept-head-name", default=None)
    parser.add_argument("--dept-head-title", default=None)
    parser.add_argument("--limit", type=int, default=0, help="Generate only the first N certificates (0 = all).")
    return parser.parse_args()


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


def to_file_uri(path_or_name: str) -> str:
    """Convert a local file path or filename to a file:// URI for browser rendering."""
    path = Path(path_or_name)
    if not path.is_absolute():
        path = Path(BASE_DIR) / path
    return path.resolve().as_uri()


def render_pdf_from_template(page, template, context, output_path):
    html = template.render(**context)
    temp_html_path = None
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8", dir=BASE_DIR) as temp_html:
            temp_html.write(html)
            temp_html_path = temp_html.name

        page.goto(Path(temp_html_path).resolve().as_uri(), wait_until="networkidle")
        page.pdf(
            path=output_path,
            print_background=True,
            prefer_css_page_size=True,
            landscape=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            page_ranges="1",
        )
    finally:
        if temp_html_path and os.path.exists(temp_html_path):
            os.remove(temp_html_path)


def normalize_name(value: str) -> str:
    cleaned = "".join(ch for ch in value if unicodedata.category(ch) != "Cf")
    return " ".join(cleaned.split())


def choose_name_font_size(name: str) -> int:
    n = len(name)
    if n <= 20:
        return 42
    if n <= 26:
        return 36
    if n <= 32:
        return 32
    return 28


def choose_team_font_size(team_line: str) -> int:
    n = len(team_line)
    if n <= 24:
        return 14
    if n <= 34:
        return 13
    return 12


def parse_participants_from_csv(csv_path: str) -> List[Dict[str, str]]:
    """Parse all participants (leader + member 2 + member 3) from CSV export."""

    def normalize_header(value):
        return "".join(ch for ch in value.lower() if ch.isalnum())

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
            raise ValueError("Could not find 'Team Name' column in input CSV")

        for row in reader:
            team = " ".join(row.get(team_col, "").split())
            for name_col, email_col in member_cols:
                if not name_col or not email_col:
                    continue

                name = normalize_name(row.get(name_col, ""))
                email = "".join(row.get(email_col, "").split())
                if name and email and "@" in email:
                    participants.append({"name": name, "team": team, "email": email})

    return participants


def parse_participants_from_json(json_path: str) -> List[Dict[str, str]]:
    """Parse participants from existing manifest-like JSON list."""
    with open(json_path, "r", encoding="utf-8") as f:
        rows = json.load(f)

    if not isinstance(rows, list):
        raise ValueError("Input JSON must be an array of participant objects")

    participants = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        name = normalize_name(str(row.get("name", "")))
        team = " ".join(str(row.get("team", "")).split())
        email = "".join(str(row.get("email", "")).split())
        if name and team:
            participants.append({"name": name, "team": team, "email": email})

    if not participants:
        raise ValueError("No valid participants found in JSON input")

    return participants


def build_context(participant, index, signers):
    team_line = f"Team: {participant['team']}"
    return {
        "background_image": to_file_uri(BACKGROUND_IMAGE),
        "left_logo": to_file_uri(LEFT_LOGO),
        "right_logo": to_file_uri(RIGHT_LOGO),
        **{k: v for k, v in TEMPLATE_TEXT.items() if k not in {"contest_date", "detail_line_2", "certificate_id_prefix"}},
        "participant_name": participant["name"],
        "detail_line_1": f"Programming Contest Â· {TEMPLATE_TEXT['contest_date']}",
        "detail_line_2": TEMPLATE_TEXT["detail_line_2"],
        "team_line": team_line,
        "name_font_size": choose_name_font_size(participant["name"]),
        "team_font_size": choose_team_font_size(team_line),
        "president_signature": to_file_uri(PRES_SIGNATURE),
        "president_name": signers["president_name"],
        "president_title": signers["president_title"],
        "dept_head_signature": to_file_uri(DH_SIGNATURE),
        "dept_head_name": signers["dept_head_name"],
        "dept_head_title": signers["dept_head_title"],
        "certificate_id": f"{TEMPLATE_TEXT['certificate_id_prefix']} / {index:03d}",
    }


def main():
    args = parse_args()
    if not os.path.exists(args.template):
        raise FileNotFoundError(f"Template not found: {args.template}")

    default_input = DEFAULT_JSON_PATH if args.source == "json" else DEFAULT_CSV_PATH
    input_path = args.input_path or default_input

    signers = load_signer_config(SIGNER_CONFIG)
    signers["president_name"] = args.president_name or signers["president_name"]
    signers["president_title"] = args.president_title or signers["president_title"]
    signers["dept_head_name"] = args.dept_head_name or signers["dept_head_name"]
    signers["dept_head_title"] = args.dept_head_title or signers["dept_head_title"]

    os.makedirs(args.output_dir, exist_ok=True)

    env = Environment(loader=FileSystemLoader(BASE_DIR), autoescape=True)
    template = env.get_template(os.path.basename(args.template))

    if args.source == "csv":
        participants = parse_participants_from_csv(input_path)
    else:
        participants = parse_participants_from_json(input_path)

    if args.limit and args.limit > 0:
        participants = participants[:args.limit]

    print(f"Found {len(participants)} participants from {args.source.upper()} input.\n")

    generated = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1123, "height": 794})

        for i, participant in enumerate(participants, 1):
            safe_name = "".join(ch for ch in participant["name"] if ch.isalnum() or ch in " _-").strip().replace(" ", "_")
            out_path = os.path.join(args.output_dir, f"{i:03d}_{safe_name}.pdf")

            context = build_context(participant, i, signers)
            render_pdf_from_template(page, template, context, out_path)

            generated.append({**participant, "pdf": out_path, "index": i, "certificate_id": context["certificate_id"]})
            print(f"  [{i:03d}] {participant['name']}  |  {participant['team']}")

        browser.close()

    with open(args.manifest, "w", encoding="utf-8") as f:
        json.dump(generated, f, indent=2, ensure_ascii=False)

    print(f"\nGenerated {len(generated)} certificates -> {args.output_dir}")
    print(f"Manifest -> {args.manifest}")


if __name__ == "__main__":
    main()
