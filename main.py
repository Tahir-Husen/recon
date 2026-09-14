#!/usr/bin/env python3
"""
recon-tool — a free-stack CLI that gathers publicly-available info
about an email address or phone number.

Built for cybersecurity coursework (offensive-security / recon phase).
Use only on data you own or are explicitly authorized to test —
see README.md for the usage & ethics note.

Usage:
    python3 main.py --email someone@example.com
    python3 main.py --phone "+91XXXXXXXXXX"
    python3 main.py --email someone@example.com --output report.json
"""

import argparse
import sys

from modules import email_recon, phone_recon, report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="recon-tool",
        description="Free-stack OSINT recon tool for an email or phone number (educational use).",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--email", help="Email address to look up")
    group.add_argument("--phone", help="Phone number to look up (include country code, e.g. +91...)")

    parser.add_argument(
        "--region",
        default="IN",
        help="Default region for phone parsing if number has no country code (default: IN)",
    )
    parser.add_argument(
        "--all-sites",
        action="store_true",
        help="For email: show every site checked, not just ones with an account found",
    )
    parser.add_argument("--output", help="Path to save the full report as JSON")

    return parser


def main() -> int:
    args = build_parser().parse_args()

    if args.email:
        data = email_recon.run_email_recon(args.email, only_used=not args.all_sites)
        report.print_email_report(data)
    else:
        data = phone_recon.run_phone_recon(args.phone, default_region=args.region)
        report.print_phone_report(data)

    if args.output:
        report.save_json(data, args.output)

    if data.get("error"):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
