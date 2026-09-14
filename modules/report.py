"""
Report module — pretty-prints recon results to the terminal and
optionally saves them as JSON.
"""

import json

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def print_email_report(data: dict) -> None:
    if RICH_AVAILABLE:
        console = Console()
        if data.get("error"):
            console.print(Panel(f"[red]{data['error']}[/red]", title=f"Email recon: {data['email']}"))
            return

        table = Table(title=f"Email recon: {data['email']}  ({data['checked_count']} sites checked)")
        table.add_column("Site / Domain", style="cyan")
        table.add_column("Account found", style="green")

        if data["used_on"]:
            for site in data["used_on"]:
                table.add_row(site, "yes")
        else:
            table.add_row("-", "no accounts found")

        console.print(table)
    else:
        print(f"\n=== Email recon: {data['email']} ===")
        if data.get("error"):
            print(f"Error: {data['error']}")
            return
        print(f"Sites checked: {data['checked_count']}")
        if data["used_on"]:
            print("Account found on:")
            for site in data["used_on"]:
                print(f"  - {site}")
        else:
            print("No accounts found on checked sites.")


def print_phone_report(data: dict) -> None:
    if RICH_AVAILABLE:
        console = Console()
        if data.get("error"):
            console.print(Panel(f"[red]{data['error']}[/red]", title=f"Phone recon: {data['number']}"))
            return

        table = Table(title=f"Phone recon: {data['number']}")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Valid", str(data["valid"]))
        table.add_row("E.164 format", data["e164"] or "-")
        table.add_row("Country/region", data["country"] or "-")
        table.add_row("Carrier", data["carrier"] or "-")
        table.add_row("Line type", data["line_type"] or "-")
        table.add_row("Timezone(s)", ", ".join(data["timezones"]) or "-")

        if data.get("numverify"):
            nv = data["numverify"]
            if "error" in nv:
                table.add_row("numverify", f"error: {nv['error']}")
            else:
                table.add_row("numverify carrier", str(nv.get("carrier", "-")))
                table.add_row("numverify line_type", str(nv.get("line_type", "-")))

        console.print(table)
    else:
        print(f"\n=== Phone recon: {data['number']} ===")
        if data.get("error"):
            print(f"Error: {data['error']}")
            return
        for key in ("valid", "e164", "country", "carrier", "line_type", "timezones"):
            print(f"{key}: {data[key]}")
        if data.get("numverify"):
            print(f"numverify: {data['numverify']}")


def save_json(data: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n[+] Full report saved to {path}")
