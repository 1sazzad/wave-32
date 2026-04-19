# WAVE-32 Certificate Generator (HTML/React + Python)

This project now uses a **single certificate design** in:
- `certificate_template.html` (used by Python PDF generator)
- `certificate_template_react.jsx` + `certificate_template.css` (React preview/app use)

All certificate fields are dynamic and filled from participant data + config.

---

## Requirements

```bash
pip install jinja2 xhtml2pdf
```

---

## Dynamic fields used in the template

These fields are rendered dynamically for every participant:
- Participant name
- Team name
- Certificate serial/ID
- Signer names/titles
- Contest/organization text constants

Main rendering logic: `generate_certificates.py`.

---

## Generate certificates with Python

### Option A: from existing JSON manifest (default)

```bash
python generate_certificates.py --source json --input cert_manifest.json
```

### Option B: from Google Form CSV

```bash
python generate_certificates.py --source csv --input responses.csv
```

### Override signers from command line

```bash
python generate_certificates.py \
  --source json \
  --president-name "Md. Sazzad Hossain Arif" \
  --president-title "President, Programming Club of IST" \
  --dept-head-name "Prof. Dr. Rahman" \
  --dept-head-title "Head, Dept. of CSE, IST"
```

Output PDFs are generated in `certificates/` and manifest is updated in `cert_manifest.json`.

---

## React template usage

Use `certificate_template_react.jsx` in your React app and pass the same data keys used in Python context.

```jsx
<CertificateTemplate data={certificateData} />
```

Style file: `certificate_template.css`.

This keeps **exact same design** between web preview and generated PDFs.
