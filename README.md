# Bank MCP Server

Ein MCP-Server der Claude an fiktive Bankdaten anbindet. Hab das gebaut um MCP zu lernen und um zu sehen wie sowas in einem regulierten Umfeld wie einer Bank aussehen könnte.

## Aufbau

Drei Schichten, weil ein direkter DB-Zugriff in der Praxis unrealistisch wäre:

```
Claude  →  MCP-Server (server.py)  →  REST-API (api.py)  →  SQLite (bank.db)
                 │
                 ▼
            Audit-Log
```

### Tools

| Tool | Was es tut |
|------|-----------|
| `konten_auflisten` | Alle Konten mit Kontostand |
| `kontostand_abfragen` | Ein bestimmtes Konto |
| `transaktionen_abfragen` | Transaktionshistorie |
| `verdaechtige_transaktionen` | Findet auffällige Aktivitäten |
| `transaktionen_nach_zeitraum` | Filtert nach Datum |
| `audit_log_anzeigen` | Wer hat wann was abgefragt |

### Testdaten

5 Konten, ~50 Transaktionen, 7 davon verdächtig. Die verdächtigen bilden echte Muster ab:

- **Smurfing** – drei Bareinzahlungen knapp unter 10.000€ an aufeinanderfolgenden Tagen
- **Offshore** – wiederkehrende Zahlungen an "Offshore Holdings Ltd."
- **Krypto** – 15.000€ an eine Kryptobörse
- **Glücksspiel** – 12.500€ ans Online-Casino

### Audit-Log

Jeder Tool-Aufruf wird mitgeschrieben:

```json
{
  "timestamp": "2025-04-20T14:32:01",
  "tool": "verdaechtige_transaktionen",
  "params": {"min_betrag": 10000},
  "success": true,
  "result_summary": "7 verdächtige Transaktionen"
}
```

## Setup

Braucht Python 3.10+.

```bash
git clone https://github.com/makaruti/bank-mcp-server.git
cd bank-mcp-server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/setup_database.py
```

Dann in zwei Terminals:

```bash
python src/api.py      # Terminal 1
python src/server.py   # Terminal 2
```

Claude Desktop Config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "bank-mcp-server": {
      "command": "/pfad/zum/projekt/.venv/bin/python",
      "args": ["/pfad/zum/projekt/src/server.py"]
    }
  }
}
```

## Was in der Praxis anders wäre

Das ist ein Prototyp, kein Produktivsystem. In echt bräuchte man mindestens:

- **Auth & Zugriffskontrolle** – nicht jeder darf alles sehen, Kundennamen müssten je nach Rolle maskiert werden
- **Regulatorik** – EU AI Act, DSGVO, BaFin/MaRisk
- **Logging** – Audit-Logs gehören in Splunk oder nen ELK Stack, nicht in ne lokale Datei
- **MCP Registry** – wenn man viele MCP-Server hat braucht man ein zentrales Verzeichnis

## Tech Stack

Python, MCP SDK, FastAPI, httpx, SQLite
