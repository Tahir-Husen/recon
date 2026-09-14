"""
Phone recon module.

Primary source: Google's `phonenumbers` library (libphonenumber port).
This works fully offline and free — no API key, no rate limit — and
gives carrier, region, line type, and timezone info derived from the
number's structure and public numbering-plan metadata.

Optional secondary source: numverify's free tier (apilayer.com), used
only if NUMVERIFY_API_KEY is set in the environment. Free tier is
capped (around 100 requests/month) so it's treated as a bonus, not a
requirement.
"""

import os

import phonenumbers
from phonenumbers import carrier, geocoder, timezone

try:
    import requests
except ImportError:  # requests is in requirements.txt, but keep this optional-safe
    requests = None


def run_phone_recon(raw_number: str, default_region: str = "IN") -> dict:
    """
    Returns a normalized dict:
    {
        "number": str,
        "valid": bool,
        "possible": bool,
        "country": str | None,
        "carrier": str | None,
        "line_type": str | None,
        "timezones": [str, ...],
        "e164": str | None,
        "numverify": dict | None,
        "error": str | None
    }
    """
    result = {
        "number": raw_number,
        "valid": False,
        "possible": False,
        "country": None,
        "carrier": None,
        "line_type": None,
        "timezones": [],
        "e164": None,
        "numverify": None,
        "error": None,
    }

    try:
        parsed = phonenumbers.parse(raw_number, default_region)
    except phonenumbers.NumberParseException as e:
        result["error"] = f"could not parse number: {e}"
        return result

    result["valid"] = phonenumbers.is_valid_number(parsed)
    result["possible"] = phonenumbers.is_possible_number(parsed)
    result["e164"] = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    result["country"] = geocoder.description_for_number(parsed, "en")
    result["carrier"] = carrier.name_for_number(parsed, "en") or None

    line_type_map = {
        phonenumbers.PhoneNumberType.MOBILE: "mobile",
        phonenumbers.PhoneNumberType.FIXED_LINE: "fixed_line",
        phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "fixed_line_or_mobile",
        phonenumbers.PhoneNumberType.TOLL_FREE: "toll_free",
        phonenumbers.PhoneNumberType.PREMIUM_RATE: "premium_rate",
        phonenumbers.PhoneNumberType.VOIP: "voip",
        phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "personal_number",
        phonenumbers.PhoneNumberType.PAGER: "pager",
        phonenumbers.PhoneNumberType.UAN: "uan",
        phonenumbers.PhoneNumberType.UNKNOWN: "unknown",
    }
    num_type = phonenumbers.number_type(parsed)
    result["line_type"] = line_type_map.get(num_type, "unknown")

    tzs = timezone.time_zones_for_number(parsed)
    result["timezones"] = list(tzs)

    api_key = os.environ.get("NUMVERIFY_API_KEY")
    if api_key and requests is not None:
        result["numverify"] = _query_numverify(result["e164"], api_key)

    return result


def _query_numverify(e164_number: str, api_key: str) -> dict:
    """Optional cross-check via numverify's free tier. Returns {} on failure."""
    number_no_plus = e164_number.lstrip("+")
    url = "http://apilayer.net/api/validate"
    params = {"access_key": api_key, "number": number_no_plus}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}
