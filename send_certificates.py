"""
ReSterT-30 Certificate Email Sender
=====================================
Reads cert_manifest.json and sends each participant their certificate by email
via Gmail (app password) or any SMTP server.

Setup (one-time):
    1. Enable 2FA on your Gmail account
    2. Generate an App Password: Google Account → Security → App Passwords
    3. Copy that 16-character password into GMAIL_APP_PASSWORD below
       (or set the environment variable GMAIL_APP_PASSWORD)

Usage:
    python send_certificates.py                  # sends to everyone not yet sent
    python send_certificates.py --test           # sends only to SENDER_EMAIL (dry run)
    python send_certificates.py --resume         # skips already-sent emails (reads sent_log.json)
"""

import json
import os
import smtplib
import sys
import time
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

# ── Gmail configuration ───────────────────────────────────────────────────────
SENDER_EMAIL      = "your_gmail@gmail.com"          # <-- change this
SENDER_NAME       = "Programming Club of IST"
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "xxxx xxxx xxxx xxxx")  # 16-char app password

# ── Email content ─────────────────────────────────────────────────────────────
EMAIL_SUBJECT = "Certificate of Participation — ReSterT 30 | Programming Club of IST"

EMAIL_BODY_TEMPLATE = """\
Dear {name},

Congratulations on participating in ReSterT — 30, the Intra-University \
Programming Contest organized by the Programming Club of IST in August 2025.

Please find your Certificate of Participation attached to this email.

We appreciate your enthusiasm and look forward to seeing you at future contests!

Best regards,
Programming Club of IST
Institute of Science and Technology, Dhaka
"""

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
MANIFEST    = os.path.join(BASE_DIR, "cert_manifest.json")
SENT_LOG    = os.path.join(BASE_DIR, "sent_log.json")

DELAY_BETWEEN_EMAILS = 2  # seconds — avoid Gmail rate limits


def load_sent_log():
    if os.path.exists(SENT_LOG):
        with open(SENT_LOG) as f:
            return set(json.load(f))
    return set()


def save_sent_log(sent_emails):
    with open(SENT_LOG, "w") as f:
        json.dump(list(sent_emails), f, indent=2)


def send_email(smtp, to_email, to_name, team_name, pdf_path):
    msg = MIMEMultipart()
    msg["From"]    = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    msg["To"]      = to_email
    msg["Subject"] = EMAIL_SUBJECT

    body = EMAIL_BODY_TEMPLATE.format(name=to_name, team=team_name)
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with open(pdf_path, "rb") as f:
        part = MIMEApplication(f.read(), Name=os.path.basename(pdf_path))
    part["Content-Disposition"] = f'attachment; filename="{os.path.basename(pdf_path)}"'
    msg.attach(part)

    smtp.sendmail(SENDER_EMAIL, to_email, msg.as_string())


def main():
    test_mode  = "--test"   in sys.argv
    resume     = "--resume" in sys.argv

    with open(MANIFEST, encoding="utf-8") as f:
        participants = json.load(f)

    sent_emails = load_sent_log() if resume else set()

    if test_mode:
        participants = [participants[0]]   # send only first entry to yourself
        participants[0]["email"] = SENDER_EMAIL
        print(f"TEST MODE — sending sample certificate to {SENDER_EMAIL}\n")

    print(f"Connecting to Gmail SMTP...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SENDER_EMAIL, GMAIL_APP_PASSWORD)
        print("Connected.\n")

        total   = len(participants)
        success = 0
        failed  = []

        for i, p in enumerate(participants, 1):
            email = p["email"].strip()
            name  = p["name"].strip()
            team  = p["team"].strip()
            pdf   = p["pdf"]

            if resume and email in sent_emails:
                print(f"  [{i:02d}/{total}] SKIP (already sent): {name}")
                continue

            if not os.path.exists(pdf):
                print(f"  [{i:02d}/{total}] MISSING PDF: {pdf}")
                failed.append({"email": email, "reason": "pdf not found"})
                continue

            try:
                send_email(smtp, email, name, team, pdf)
                sent_emails.add(email)
                save_sent_log(sent_emails)
                success += 1
                print(f"  [{i:02d}/{total}] ✓ Sent → {name} <{email}>")
            except Exception as e:
                print(f"  [{i:02d}/{total}] ✗ FAILED → {email}: {e}")
                failed.append({"email": email, "reason": str(e)})

            if i < total:
                time.sleep(DELAY_BETWEEN_EMAILS)

    print(f"\n─────────────────────────────────")
    print(f"Sent:   {success}")
    print(f"Failed: {len(failed)}")
    if failed:
        print("\nFailed list:")
        for f in failed:
            print(f"  {f['email']} — {f['reason']}")
    print(f"\nSent log saved to: {SENT_LOG}")


if __name__ == "__main__":
    main()
