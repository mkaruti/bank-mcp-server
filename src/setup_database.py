import sqlite3
import os
from datetime import datetime, timedelta
import random
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "bank.db")

def create_tables(cursor):
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS konten (
                kontonummer TEXT PRIMARY KEY,
                inhaber TEXT NOT NULL,
                iban TEXT NOT NULL UNIQUE,
                kontostand REAL NOT NULL,
                kontotyp TEXT NOT NULL,
                eroeffnet_am TEXT NOT NULL
            )
        """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS transaktionen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kontonummer TEXT NOT NULL,
                betrag REAL NOT NULL,
                empfaenger TEXT NOT NULL,
                verwendungszweck TEXT NOT NULL,
                datum TEXT NOT NULL,
                kategorie TEXT NOT NULL,
                verdaechtig INTEGER DEFAULT 0,
                FOREIGN KEY (kontonummer) REFERENCES konten(kontonummer)
            )
        """)

def seed_konten(cursor):
    konten = [
        ("1001", "Anna Müller", "DE89370400440532013000", 15420.50, "Girokonto", "2019-03-15"),
        ("1002", "Thomas Weber", "DE27100777770209299700", 48230.00, "Girokonto", "2020-07-22"),
        ("1003", "Sofia Petrov", "DE60500105175407324931", 3150.75, "Girokonto", "2021-01-10"),
        ("1004", "Markus Schmidt", "DE44500105175407329876", 125800.00, "Geschäftskonto", "2018-11-05"),
        ("1005", "Elena Fischer", "DE91100000000123456789", 9870.30, "Girokonto", "2022-04-18"),
    ]

    cursor.executemany(
        "INSERT OR REPLACE INTO konten VALUES (?, ?, ?, ?, ?, ?)",
        konten
    )
def seed_transaktionen(cursor):
    kategorien_normal = [
        ("Supermarkt", "REWE Einkauf", -45.80, -180.00),
        ("Supermarkt", "EDEKA Lebensmittel", -30.00, -120.00),
        ("Miete", "Mietzahlung Wohnung", -850.00, -1200.00),
        ("Gehalt", "Gehaltseingang", 2800.00, 4500.00),
        ("Restaurant", "Restaurant Da Luigi", -25.00, -85.00),
        ("Transport", "Deutsche Bahn Ticket", -35.00, -120.00),
        ("Versicherung", "Allianz Versicherung", -89.90, -89.90),
        ("Telekommunikation", "Vodafone Mobilfunk", -39.99, -39.99),
        ("Energie", "Stadtwerke Strom/Gas", -95.00, -180.00),
        ("Shopping", "Amazon Bestellung", -20.00, -150.00),
        ("Freizeit", "Netflix Abo", -12.99, -12.99),
        ("Freizeit", "Spotify Premium", -9.99, -9.99),
    ]
    verdaechtige = [
        ("1002", -15000.00, "Kryptobörse CoinEx Ltd.", "Überweisung Krypto", "Krypto", "2025-04-10"),
        ("1004", -28500.00, "Offshore Holdings Ltd.", "Beratungshonorar Q1", "Auslandsüberweisung", "2025-03-22"),
        ("1004", -32000.00, "Offshore Holdings Ltd.", "Beratungshonorar Q2", "Auslandsüberweisung", "2025-04-15"),
        ("1003", 9999.00, "Unbekannt", "Bareinzahlung", "Bareinzahlung", "2025-04-02"),
        ("1003", 9998.00, "Unbekannt", "Bareinzahlung", "Bareinzahlung", "2025-04-03"),
        ("1003", 9997.00, "Unbekannt", "Bareinzahlung", "Bareinzahlung", "2025-04-04"),
        ("1001", -12500.00, "Gaming Paradise Ltd.", "Online Casino Einzahlung", "Glücksspiel", "2025-04-20"),
    ]

    transaktionen = []
    kontonummern = ["1001", "1002", "1003", "1004", "1005"]
    start_datum = datetime(2025, 2, 1)

    for konto in kontonummern:
        for i in range(8):
            kat = random.choice(kategorien_normal)
            kategorie, verwendungszweck, betrag_min, betrag_max = kat

            if betrag_min == betrag_max:
                betrag = betrag_min
            else:
                betrag = round(random.uniform(
                    min(betrag_min, betrag_max),
                    max(betrag_min, betrag_max)
                ), 2)

            datum = start_datum + timedelta(days=random.randint(0, 90))

            transaktionen.append((
                konto, betrag, verwendungszweck.split(" ")[0] + " GmbH",
                verwendungszweck, datum.strftime("%Y-%m-%d"),
                kategorie, 0
            ))

    for v in verdaechtige:
        transaktionen.append((v[0], v[1], v[2], v[3], v[5], v[4], 1))

    cursor.executemany(
        "INSERT INTO transaktionen (kontonummer, betrag, empfaenger, verwendungszweck, datum, kategorie, verdaechtig) VALUES (?, ?, ?, ?, ?, ?, ?)",
        transaktionen
    )

def main():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    create_tables(cursor)
    seed_konten(cursor)
    seed_transaktionen(cursor)

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM konten")
    print(f"Konten erstellt: {cursor.fetchone()[0]}")

    cursor.execute("SELECT COUNT(*) FROM transaktionen")
    print(f"Transaktionen erstellt: {cursor.fetchone()[0]}")

    cursor.execute("SELECT COUNT(*) FROM transaktionen WHERE verdaechtig = 1")
    print(f"Davon verdächtig: {cursor.fetchone()[0]}")

    conn.close()
    print(f"\nDatenbank erstellt: {DB_PATH}")


if __name__ == "__main__":
    main()

