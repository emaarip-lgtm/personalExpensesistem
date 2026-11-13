#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema di Gestione delle Spese Personali e del Budget
Applicazione console in Python 3 + database SQL (SQLite, libreria standard).

Uso:
    python3 main.py            # usa/crea spese.db (con dati di esempio)
    python3 main.py --vuoto    # se il DB non esiste lo crea senza dati di esempio
"""

import os
import sqlite3
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_FILE = os.path.join(BASE_DIR, "..", "sql", "database.sql")
DB_FILE = os.path.join(BASE_DIR, "..", "spese.db")
MARCATORE_DATI = "-- ==== DATI DI ESEMPIO ===="


# ----------------------------------------------------------------------
# Database
# ----------------------------------------------------------------------
def connetti(solo_schema=False):
    """Apre la connessione; se il file DB non esiste lo crea da database.sql."""
    nuovo = not os.path.exists(DB_FILE)
    conn = sqlite3.connect(DB_FILE)
    if nuovo:
        with open(SQL_FILE, encoding="utf-8") as f:
            script = f.read()
        if solo_schema:
            script = script.split(MARCATORE_DATI)[0]
        conn.executescript(script)
        conn.commit()
    conn.execute("PRAGMA foreign_keys = ON")  # abilita i vincoli di chiave esterna
    return conn


# ----------------------------------------------------------------------
# Funzioni di input / validazione
# ----------------------------------------------------------------------
def leggi_testo(prompt):
    return input(prompt).strip()


def leggi_importo(prompt):
    """Restituisce un float (accetta anche la virgola) oppure None se non numerico."""
    valore = input(prompt).strip().replace(",", ".")
    try:
        numero = float(valore)
    except ValueError:
        return None
    if numero != numero or numero in (float("inf"), float("-inf")):  # NaN / inf
        return None
    return numero


def data_valida(testo):
    try:
        datetime.strptime(testo, "%Y-%m-%d")
        return len(testo) == 10
    except ValueError:
        return False


def mese_valido(testo):
    try:
        datetime.strptime(testo, "%Y-%m")
        return len(testo) == 7
    except ValueError:
        return False


def trova_categoria(conn, nome):
    """Restituisce (id, nome) della categoria o None se non esiste."""
    return conn.execute(
        "SELECT id_categoria, nome FROM categorie WHERE nome = ?", (nome,)
    ).fetchone()


# ----------------------------------------------------------------------
# MODULO 1 - Gestione Categorie
# ----------------------------------------------------------------------
def gestione_categorie(conn):
    nome = leggi_testo("Nome della categoria: ")
    if nome == "":
        print("Errore: il nome della categoria non può essere vuoto.")
        return
    if trova_categoria(conn, nome):                      # SQL SELECT
        print("La categoria esiste già.")
        return
    conn.execute("INSERT INTO categorie (nome) VALUES (?)", (nome,))  # SQL INSERT
    conn.commit()
    print("Categoria inserita correttamente.")


# ----------------------------------------------------------------------
# MODULO 2 - Inserimento Spesa
# ----------------------------------------------------------------------
def inserisci_spesa(conn):
    data = leggi_testo("Data (YYYY-MM-DD): ")
    importo = leggi_importo("Importo: ")
    nome_cat = leggi_testo("Nome della categoria: ")
    descrizione = leggi_testo("Descrizione (facoltativa): ")

    if not data_valida(data):
        print("Errore: la data non è valida (formato richiesto YYYY-MM-DD).")
        return
    if importo is None:
        print("Errore: l'importo deve essere un numero.")
        return
    if importo <= 0:
        print("Errore: l'importo deve essere maggiore di zero.")
        return
    cat = trova_categoria(conn, nome_cat)                # SQL SELECT
    if cat is None:
        print("Errore: la categoria non esiste.")
        return

    conn.execute(                                        # SQL INSERT (con FK)
        "INSERT INTO spese (data, importo, id_categoria, descrizione) "
        "VALUES (?, ?, ?, ?)",
        (data, importo, cat[0], descrizione or None),
    )
    conn.commit()
    print("Spesa inserita correttamente.")


# ----------------------------------------------------------------------
# MODULO 3 - Budget Mensile
# ----------------------------------------------------------------------
def definisci_budget(conn):
    mese = leggi_testo("Mese (YYYY-MM): ")
    nome_cat = leggi_testo("Nome della categoria: ")
    importo = leggi_importo("Importo del budget: ")

    if not mese_valido(mese):
        print("Errore: il mese non è valido (formato richiesto YYYY-MM).")
        return
    if importo is None:
        print("Errore: l'importo deve essere un numero.")
        return
    if importo <= 0:
        print("Errore: il budget deve essere maggiore di zero.")
        return
    cat = trova_categoria(conn, nome_cat)
    if cat is None:
        print("Errore: la categoria non esiste.")
        return

    # Inserimento oppure aggiornamento se esiste già (mese, categoria)
    conn.execute(
        "INSERT INTO budget (mese, id_categoria, importo_budget) VALUES (?, ?, ?) "
        "ON CONFLICT(mese, id_categoria) DO UPDATE SET importo_budget = excluded.importo_budget",
        (mese, cat[0], importo),
    )
    conn.commit()
    print("Budget mensile salvato correttamente.")


# ----------------------------------------------------------------------
# MODULO 4 - Report
# ----------------------------------------------------------------------
def report_totale_per_categoria(conn):
    righe = conn.execute(
        """SELECT c.nome, SUM(s.importo)
           FROM categorie c
           JOIN spese s ON s.id_categoria = c.id_categoria
           GROUP BY c.id_categoria
           ORDER BY SUM(s.importo) DESC"""
    ).fetchall()
    if not righe:
        print("Nessuna spesa registrata.")
        return
    print(f"\n{'Categoria':<20}{'Totale Speso':>14}")
    print("-" * 34)
    for nome, totale in righe:
        print(f"{nome:<20}{totale:>14.2f}")


def report_spese_vs_budget(conn):
    righe = conn.execute(
        """SELECT b.mese, c.nome, b.importo_budget,
                  COALESCE(SUM(s.importo), 0)
           FROM budget b
           JOIN categorie c ON c.id_categoria = b.id_categoria
           LEFT JOIN spese s ON s.id_categoria = b.id_categoria
                            AND substr(s.data, 1, 7) = b.mese
           GROUP BY b.id_budget
           ORDER BY b.mese, c.nome"""
    ).fetchall()
    if not righe:
        print("Nessun budget definito.")
        return
    for mese, nome, budget, speso in righe:
        if speso > budget:
            stato = "SUPERAMENTO BUDGET"
        else:
            stato = "Nel budget"
        print(f"\nMese: {mese}")
        print(f"Categoria: {nome}")
        print(f"Budget: {budget:g}")
        print(f"Speso: {speso:g}")
        print(f"Stato: {stato}")


def report_elenco_spese(conn):
    righe = conn.execute(
        """SELECT s.data, c.nome, s.importo, COALESCE(s.descrizione, '')
           FROM spese s
           JOIN categorie c ON c.id_categoria = s.id_categoria
           ORDER BY s.data, s.id_spesa"""
    ).fetchall()
    if not righe:
        print("Nessuna spesa registrata.")
        return
    print(f"\n{'Data':<12}{'Categoria':<16}{'Importo':>10}  Descrizione")
    print("-" * 62)
    for data, nome, importo, desc in righe:
        print(f"{data:<12}{nome:<16}{importo:>10.2f}  {desc}")


def visualizza_report(conn):
    while True:
        print("\n----- MENU REPORT -----")
        print("1. Totale spese per categoria")
        print("2. Spese mensili vs budget")
        print("3. Elenco completo delle spese ordinate per data")
        print("4. Ritorna al menu principale")
        print("-----------------------")
        scelta = input("Inserisci la tua scelta: ").strip()
        match scelta:
            case "1":
                report_totale_per_categoria(conn)
            case "2":
                report_spese_vs_budget(conn)
            case "3":
                report_elenco_spese(conn)
            case "4":
                return
            case _:
                print("Scelta non valida. Riprovare.")


# ----------------------------------------------------------------------
# Menu principale
# ----------------------------------------------------------------------
def main():
    conn = connetti(solo_schema="--vuoto" in sys.argv)
    print("Benvenuto nel Sistema di Gestione delle Spese Personali!")
    while True:
        print("\n-------------------------")
        print("SISTEMA SPESE PERSONALI")
        print("-------------------------")
        print("1. Gestione Categorie")
        print("2. Inserisci Spesa")
        print("3. Definisci Budget Mensile")
        print("4. Visualizza Report")
        print("5. Esci")
        print("-------------------------")
        scelta = input("Inserisci la tua scelta: ").strip()
        match scelta:
            case "1":
                gestione_categorie(conn)
            case "2":
                inserisci_spesa(conn)
            case "3":
                definisci_budget(conn)
            case "4":
                visualizza_report(conn)
            case "5":
                print("Arrivederci!")
                break
            case _:
                print("Scelta non valida. Riprovare.")
    conn.close()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nUscita dal programma.")
