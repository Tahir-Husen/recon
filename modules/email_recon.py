"""
Email recon module.

Wraps the open-source `holehe` tool, which checks whether an email
address is registered on 100+ websites/services by abusing public
"forgot password" / "signup" endpoints that leak account existence.

holehe must be installed (see requirements.txt). It ships a CLI
entry point, so we shell out to it and parse the CSV it produces
rather than reimplementing its site checks.
"""

import csv
import os
import shutil
import subprocess
import tempfile


def check_holehe_installed() -> bool:
    return shutil.which("holehe") is not None


def run_email_recon(email: str, only_used: bool = True, timeout: int = 120) -> dict:
    """
    Runs holehe against an email address and returns a normalized dict:
    {
        "email": str,
        "tool": "holehe",
        "available": bool,          # whether holehe ran successfully
        "used_on": [str, ...],      # sites where the email has an account
        "checked_count": int,       # total sites checked
        "error": str | None
    }
    """
    result = {
        "email": email,
        "tool": "holehe",
        "available": False,
        "used_on": [],
        "checked_count": 0,
        "error": None,
    }

    if not check_holehe_installed():
        result["error"] = (
            "holehe is not installed or not on PATH. "
            "Install it with: pip install holehe"
        )
        return result

    with tempfile.TemporaryDirectory() as tmp_dir:
        csv_path = os.path.join(tmp_dir, "holehe_out.csv")
        cmd = ["holehe", email, "--no-color", "-C", csv_path]
        if only_used:
            cmd.append("--only-used")

        try:
            subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            result["error"] = f"holehe timed out after {timeout}s"
            return result
        except FileNotFoundError:
            result["error"] = "holehe executable not found"
            return result

        if not os.path.exists(csv_path):
            result["error"] = "holehe did not produce output (check network access / holehe install)"
            return result

        try:
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        except Exception as e:
            result["error"] = f"failed to parse holehe CSV output: {e}"
            return result

        result["available"] = True
        result["checked_count"] = len(rows)

        for row in rows:
            # holehe CSV columns typically include: email, domain/name, exists, ...
            exists_val = str(row.get("exists", row.get("Exists", ""))).strip().lower()
            domain_val = row.get("domain") or row.get("name") or row.get("module") or "unknown"
            if exists_val in ("true", "1", "yes"):
                result["used_on"].append(domain_val)

    return result
