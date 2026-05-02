from fastapi import FastAPI, HTTPException
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "bank.db")

app = FastAPI(title="Banking API")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/konten")
def konten_auflisten():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM konten ORDER BY kontonummer")
    konten = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return konten

@app.get("/konten/{kontonummer}")
def konto_abrufen(kontonummer: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM konten WHERE kontonummer = ?", (kontonummer,))
    konto = cursor.fetchone()
    conn.close()

    if not konto:
        raise HTTPException(status_code=404, detail=f"Konto {kontonummer} nicht gefunden")

    return dict(konto)

@app.get("/konten/{kontonummer}/transaktionen")
def transaktionen_abrufen(kontonummer: str, limit: int = 20):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM transaktionen WHERE kontonummer = ? ORDER BY datum DESC LIMIT ?",
        (kontonummer, limit)
    )
    transaktionen = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return transaktionen

@app.get("/transaktionen/verdaechtig")
def verdaechtige_transaktionen(min_betrag: float = 0):
    conn = get_db_connection()
    cursor = conn.cursor()

    if min_betrag > 0:
        cursor.execute(
            "SELECT t.*, k.inhaber FROM transaktionen t "
            "JOIN konten k ON t.kontonummer = k.kontonummer "
            "WHERE t.verdaechtig = 1 AND ABS(t.betrag) >= ? "
            "ORDER BY t.datum DESC",
            (min_betrag,)
        )
    else:
        cursor.execute(
            "SELECT t.*, k.inhaber FROM transaktionen t "
            "JOIN konten k ON t.kontonummer = k.kontonummer "
            "WHERE t.verdaechtig = 1 "
            "ORDER BY t.datum DESC"
        )

    transaktionen = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return transaktionen


@app.get("/transaktionen")
def transaktionen_nach_zeitraum(von: str, bis: str, kontonummer: str = ""):
    conn = get_db_connection()
    cursor = conn.cursor()

    if kontonummer:
        cursor.execute(
            "SELECT t.*, k.inhaber FROM transaktionen t "
            "JOIN konten k ON t.kontonummer = k.kontonummer "
            "WHERE t.datum BETWEEN ? AND ? AND t.kontonummer = ? "
            "ORDER BY t.datum DESC",
            (von, bis, kontonummer)
        )
    else:
        cursor.execute(
            "SELECT t.*, k.inhaber FROM transaktionen t "
            "JOIN konten k ON t.kontonummer = k.kontonummer "
            "WHERE t.datum BETWEEN ? AND ? "
            "ORDER BY t.datum DESC",
            (von, bis)
        )

    transaktionen = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return transaktionen



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)



