# recon-tool

A free-stack CLI recon tool built for cybersecurity coursework. Give
it an email address or a phone number, it aggregates what's publicly
discoverable about it — which sites an email is registered on, and
the carrier/region/line-type info a phone number reveals.

Everything runs on free, open-source components. No paid APIs required.

## What it uses

| Input | Source | Cost | Needs internet |
|---|---|---|---|
| Email | [`holehe`](https://github.com/megadose/holehe) — checks 100+ sites for a registered account via their public signup/reset endpoints | Free, open-source | Yes |
| Phone | [`phonenumbers`](https://github.com/daviddrysdale/python-phonenumbers) (Google's libphonenumber) — carrier, region, line type, timezone | Free, fully offline | No |
| Phone (optional) | [numverify](https://numverify.com) free tier — cross-check carrier/line type | Free tier (~100 req/month), needs an API key | Yes |

## Requirements

- Python 3.8+
- pip
- Linux (developed/tested on Linux; should also run on macOS)

## Installation

```bash
# 1. Unzip / clone the project and enter it
unzip osint-recon-tool.zip
cd osint-recon-tool

# 2. Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# If your system blocks global installs and you're not using a venv:
pip install -r requirements.txt --break-system-packages
```

`requirements.txt`:
```
holehe>=1.61
phonenumbers>=8.13.0
requests>=2.31.0
rich>=13.7.0
```

Optional — enable the numverify cross-check for phone lookups:

```bash
export NUMVERIFY_API_KEY="your_free_key"   # get one at numverify.com
```

## Usage

```bash
# Email lookup
python3 main.py --email someone@example.com

# Phone lookup (include country code)
python3 main.py --phone "+91XXXXXXXXXX"

# Show every site holehe checked, not just hits
python3 main.py --email someone@example.com --all-sites

# Save the full report as JSON
python3 main.py --email someone@example.com --output report.json

# Change default region used when a phone number has no country code
python3 main.py --phone "9876543210" --region US
```

## Project structure

```
osint-recon-tool/
├── main.py                 # CLI entry point
├── config.py                # optional API key handling (env vars)
├── requirements.txt
├── LICENSE
├── README.md
└── modules/
    ├── email_recon.py       # holehe wrapper
    ├── phone_recon.py       # phonenumbers + optional numverify
    └── report.py            # terminal output + JSON export
```

## Notes

- `holehe` needs real internet access to the sites it checks — in a
  sandboxed/restricted network, email lookups fail cleanly with an
  error instead of crashing. Phone lookups work fully offline since
  they rely on numbering-plan metadata, not live queries.

## Ethics & scope

This is a **reconnaissance/offensive-security tool** built for
coursework. Treat it accordingly:

- Only run it against your own accounts/numbers, or targets you have
  explicit written authorization to test.
- Don't use it to gather info on people without their consent — that
  crosses from "recon exercise" into harassment/stalking territory,
  which is illegal in most jurisdictions regardless of intent.
- If you write this up for your course, document scope and
  authorization the same way a real pentest report would.

## License

MIT — see [LICENSE](LICENSE).
