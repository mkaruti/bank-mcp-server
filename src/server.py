from mcp.server.fastmcp import FastMCP
import httpx
import json
import os
from datetime import datetime

API_BASE_URL = "http://127.0.0.1:8000"
LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "logs", "audit.log")

mcp = FastMCP("Bank MCP Server")


def log_audit(tool_name: str, params: dict, success: bool, result_summary: str = ""):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    entry = {
        "timestamp": datetime.now().isoformat(),
        "tool": tool_name,
        "params": params,
        "success": success,
        "result_summary": result_summary
    }

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


@mcp.tool()
def konten_auflisten() -> str:
    """Listet alle Bankkonten mit Kontonummer, Inhaber, IBAN und aktuellem Kontostand auf."""
    response = httpx.get(f"{API_BASE_URL}/konten")
    konten = response.json()

    if not konten:
        log_audit("konten_auflisten", {}, True, "Keine Konten gefunden")
        return "Keine Konten gefunden."

    lines = []
    for k in konten:
        lines.append(
            f"Konto {k['kontonummer']} | {k['inhaber']} | {k['kontotyp']}\n"
            f"  IBAN: {k['iban']}\n"
            f"  Kontostand: {k['kontostand']} €\n"
        )

    log_audit("konten_auflisten", {}, True, f"{len(konten)} Konten abgerufen")
    return "\n".join(lines)


@mcp.tool()
def kontostand_abfragen(kontonummer: str) -> str:
    """
    Fragt den Kontostand eines bestimmten Kontos ab.

    Args:
        kontonummer: Die Kontonummer des abzufragenden Kontos (z.B. "1001")
    """
    response = httpx.get(f"{API_BASE_URL}/konten/{kontonummer}")

    if response.status_code == 404:
        log_audit("kontostand_abfragen", {"kontonummer": kontonummer}, True, "Konto nicht gefunden")
        return f"Konto {kontonummer} wurde nicht gefunden."

    konto = response.json()
    log_audit("kontostand_abfragen", {"kontonummer": kontonummer}, True, f"Kontostand: {konto['kontostand']}")
    return (
        f"Konto {konto['kontonummer']} – {konto['inhaber']}\n"
        f"Typ: {konto['kontotyp']}\n"
        f"IBAN: {konto['iban']}\n"
        f"Kontostand: {konto['kontostand']} €\n"
        f"Eröffnet am: {konto['eroeffnet_am']}"
    )


@mcp.tool()
def transaktionen_abfragen(kontonummer: str, limit: int = 20) -> str:
    """
    Zeigt die Transaktionen eines bestimmten Kontos an.

    Args:
        kontonummer: Die Kontonummer (z.B. "1001")
        limit: Maximale Anzahl der Transaktionen (Standard: 20)
    """
    response = httpx.get(
        f"{API_BASE_URL}/konten/{kontonummer}/transaktionen",
        params={"limit": limit}
    )
    transaktionen = response.json()

    if not transaktionen:
        log_audit("transaktionen_abfragen", {"kontonummer": kontonummer, "limit": limit}, True, "Keine Transaktionen")
        return f"Keine Transaktionen für Konto {kontonummer} gefunden."

    lines = [f"=== Transaktionen für Konto {kontonummer} ===\n"]
    for t in transaktionen:
        flag = " ⚠️ VERDÄCHTIG" if t['verdaechtig'] else ""
        lines.append(
            f"[{t['datum']}] {t['betrag']} € | {t['empfaenger']}\n"
            f"  Verwendungszweck: {t['verwendungszweck']}\n"
            f"  Kategorie: {t['kategorie']}{flag}\n"
        )

    log_audit("transaktionen_abfragen", {"kontonummer": kontonummer, "limit": limit}, True,
              f"{len(transaktionen)} Transaktionen abgerufen")
    return "\n".join(lines)


@mcp.tool()
def verdaechtige_transaktionen(min_betrag: float = 0) -> str:
    """
    Findet alle als verdächtig markierten Transaktionen.
    Verdächtig sind z.B. hohe Bareinzahlungen, Offshore-Überweisungen oder Krypto-Transfers.

    Args:
        min_betrag: Optionaler Mindestbetrag (absolut) zum Filtern (Standard: 0 = alle)
    """
    response = httpx.get(
        f"{API_BASE_URL}/transaktionen/verdaechtig",
        params={"min_betrag": min_betrag}
    )
    transaktionen = response.json()

    if not transaktionen:
        log_audit("verdaechtige_transaktionen", {"min_betrag": min_betrag}, True, "Keine verdächtigen Transaktionen")
        return "Keine verdächtigen Transaktionen gefunden."

    lines = ["=== ⚠️ Verdächtige Transaktionen ===\n"]
    gesamt_betrag = 0

    for t in transaktionen:
        gesamt_betrag += abs(t['betrag'])
        lines.append(
            f"[{t['datum']}] Konto {t['kontonummer']} ({t['inhaber']})\n"
            f"  Betrag: {t['betrag']} €\n"
            f"  Empfänger: {t['empfaenger']}\n"
            f"  Verwendungszweck: {t['verwendungszweck']}\n"
            f"  Kategorie: {t['kategorie']}\n"
        )

    lines.append(f"\nAnzahl: {len(transaktionen)}")
    lines.append(f"Gesamtvolumen: {gesamt_betrag} €")

    log_audit("verdaechtige_transaktionen", {"min_betrag": min_betrag}, True,
              f"{len(transaktionen)} verdächtige Transaktionen, Volumen: {gesamt_betrag}")
    return "\n".join(lines)


@mcp.tool()
def transaktionen_nach_zeitraum(von: str, bis: str, kontonummer: str = "") -> str:
    """
    Filtert Transaktionen nach einem bestimmten Zeitraum.

    Args:
        von: Startdatum im Format YYYY-MM-DD (z.B. "2025-03-01")
        bis: Enddatum im Format YYYY-MM-DD (z.B. "2025-04-30")
        kontonummer: Optional – auf ein bestimmtes Konto filtern
    """
    params = {"von": von, "bis": bis}
    if kontonummer:
        params["kontonummer"] = kontonummer

    response = httpx.get(f"{API_BASE_URL}/transaktionen", params=params)
    transaktionen = response.json()

    if not transaktionen:
        log_audit("transaktionen_nach_zeitraum", {"von": von, "bis": bis, "kontonummer": kontonummer}, True,
                  "Keine Transaktionen im Zeitraum")
        return f"Keine Transaktionen im Zeitraum {von} bis {bis} gefunden."

    lines = [f"=== Transaktionen von {von} bis {bis} ===\n"]
    einnahmen = 0
    ausgaben = 0

    for t in transaktionen:
        flag = " ⚠️ VERDÄCHTIG" if t['verdaechtig'] else ""
        if t['betrag'] > 0:
            einnahmen += t['betrag']
        else:
            ausgaben += abs(t['betrag'])

        lines.append(
            f"[{t['datum']}] Konto {t['kontonummer']} ({t['inhaber']})\n"
            f"  {t['betrag']} € | {t['empfaenger']}\n"
            f"  {t['verwendungszweck']} | {t['kategorie']}{flag}\n"
        )

    lines.append(f"\nEinnahmen: {einnahmen} €")
    lines.append(f"Ausgaben: {ausgaben} €")
    lines.append(f"Saldo: {einnahmen - ausgaben} €")

    log_audit("transaktionen_nach_zeitraum", {"von": von, "bis": bis, "kontonummer": kontonummer}, True,
              f"{len(transaktionen)} Transaktionen im Zeitraum")
    return "\n".join(lines)


@mcp.tool()
def audit_log_anzeigen(anzahl: int = 20) -> str:
    """
    Zeigt die letzten Einträge aus dem Audit-Log an.
    Jeder Zugriff auf Bankdaten wird hier protokolliert.

    Args:
        anzahl: Anzahl der letzten Log-Einträge (Standard: 20)
    """
    if not os.path.exists(LOG_PATH):
        return "Noch keine Audit-Einträge vorhanden."

    with open(LOG_PATH, "r", encoding="utf-8") as f:
        all_lines = f.readlines()

    entries = all_lines[-anzahl:]

    lines = [f"=== Audit-Log (letzte {len(entries)} Einträge) ===\n"]
    for entry_str in entries:
        entry = json.loads(entry_str)
        status = "✅" if entry["success"] else "❌"
        params_str = json.dumps(entry["params"], ensure_ascii=False) if entry["params"] else "keine"
        lines.append(
            f"[{entry['timestamp']}] {status} {entry['tool']}\n"
            f"  Parameter: {params_str}\n"
            f"  Ergebnis: {entry['result_summary']}\n"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()