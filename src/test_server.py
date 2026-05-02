from server import (
    konten_auflisten,
    kontostand_abfragen,
    transaktionen_abfragen,
    verdaechtige_transaktionen,
    transaktionen_nach_zeitraum,
    audit_log_anzeigen
)

print("=== Test 1: Konten auflisten ===")
print(konten_auflisten())

print("\n=== Test 2: Kontostand abfragen ===")
print(kontostand_abfragen("1003"))

print("\n=== Test 3: Transaktionen abfragen ===")
print(transaktionen_abfragen("1001", 3))

print("\n=== Test 4: Verdächtige Transaktionen ===")
print(verdaechtige_transaktionen())

print("\n=== Test 5: Zeitraum ===")
print(transaktionen_nach_zeitraum("2025-04-01", "2025-04-30"))

print("\n=== Test 6: Audit-Log ===")
print(audit_log_anzeigen())
