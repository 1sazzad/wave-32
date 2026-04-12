# ReSterT-30 Certificate Generator & Sender

ICPC-style participation certificates for the ReSterT-30 programming contest.
Generates individual PDFs and sends them by email automatically.

---

## Folder structure

```
restart30_certs/
├── generate_certificates.py   # Generates all PDFs
├── send_certificates.py       # Sends emails with PDF attachments
├── responses.csv              # Google Form export (participant data)
├── pcist_logo.png             # pcIST club logo
├── ist_logo.png               # IST institute logo
├── signature_president.png    # President's signature (replace with real)
├── signature_depthead.png     # Dept. Head's signature (replace with real)
├── certificates/              # Generated PDFs go here (auto-created)
├── cert_manifest.json         # Auto-generated: participant list + PDF paths
└── sent_log.json              # Auto-generated: tracks sent emails
```

---

## Requirements

```bash
pip install reportlab pillow
```

---

## Step 1 — Replace signatures

Collect clean signature images:
- Ask each signer to sign on plain white paper with a dark pen
- Photograph or scan it (clear light, no shadows)
- Crop tightly around the signature
- Save as PNG (transparent background preferred)

Replace these two files:
```
signature_president.png   ← President's signature
signature_depthead.png    ← Dept. Head's signature
```

---

## Step 2 — Generate certificates

**Basic (uses defaults in the script):**
```bash
python generate_certificates.py
```

**With custom signer names (recommended each year):**
```bash
python generate_certificates.py \
  "President Name" \
  "President Title" \
  "Dept Head Name" \
  "Dept Head Title"
```

Example:
```bash
python generate_certificates.py \
  "Md. Sazzad Hossain Arif" \
  "President, Programming Club of IST" \
  "Prof. Dr. Rahman" \
  "Head, Dept. of CSE, IST"
```

Output: `certificates/NNN_Participant_Name.pdf` for every participant.

---

## Step 3 — Configure email sender

Open `send_certificates.py` and update:
```python
SENDER_EMAIL       = "your_gmail@gmail.com"
GMAIL_APP_PASSWORD = "xxxx xxxx xxxx xxxx"   # Gmail App Password (not your login password)
```

**How to get a Gmail App Password:**
1. Enable 2FA on your Google account
2. Go to: Google Account → Security → App Passwords
3. Create a new app password → copy the 16-character code
4. Paste it into `GMAIL_APP_PASSWORD`

You can also set it as an environment variable instead:
```bash
export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"
```

---

## Step 4 — Send emails

**Send test email to yourself first:**
```bash
python send_certificates.py --test
```

**Send to all participants:**
```bash
python send_certificates.py
```

**Resume if interrupted (skips already-sent emails):**
```bash
python send_certificates.py --resume
```

---

## Updating for a new contest year

1. Replace `responses.csv` with the new Google Form export
2. Replace `signature_president.png` and `signature_depthead.png` if signers changed
3. Edit the contest name/date inside `generate_certificates.py`:
   - Search for `"ReSterT — 30"` and `"August 2025"` → update accordingly
4. Run `generate_certificates.py` with the new signer names
5. Run `send_certificates.py`

---

## Notes

- One PDF is generated per participant (all 3 members per team, not just leaders)
- Certificate serial number format: `PCIST / ReSterT-30 / 2025 / NNN`
- If a participant's email is invalid (e.g., missing `.com`), it will appear in the failed list
- `sent_log.json` tracks who was emailed — safe to re-run with `--resume` if interrupted
