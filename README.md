# PersonalExpenseSystem

Sistema di gestione delle spese personali e del budget, da console.
Scritto in **Python 3** con database relazionale **SQL (SQLite)**.

## Requisiti per l'esecuzione

- **Interprete:** Python 3.10 o superiore (si usa l'istruzione `match`, equivalente dello `switch`)
- **Librerie:** solo libreria standard (`sqlite3`, `datetime`, `os`, `sys`). Nessuna installazione aggiuntiva.
- **Database:** SQLite, incluso in Python. Non serve alcun server.

Verifica la versione con: `python3 --version`

## Istruzioni di esecuzione

Nessuna compilazione richiesta (Python è interpretato).

1. Clona il repository ed entra nella cartella:
   ```
   git clone https://github.com/nomeutente/PersonalExpenseSystem
   cd PersonalExpenseSystem
   ```
2. Avvia il programma con il comando esatto:
   ```
   python3 src/main.py
   ```
   (su Windows: `python src/main.py`)

Al primo avvio il file `spese.db` viene creato automaticamente a partire da `sql/database.sql`
(schema + dati di esempio). Per partire con un database vuoto:
```
python3 src/main.py --vuoto
```
Per riportare il database allo stato iniziale basta cancellare `spese.db`.

## Struttura del repository

```
PersonalExpenseSystem/
├── src/main.py            # codice sorgente
├── sql/database.sql       # CREATE TABLE + INSERT di esempio
├── demo/demo_video.mp4    # video dimostrativo
└── README.md
```

## Funzionalità

1. **Gestione Categorie** – inserimento con controllo di nome vuoto e duplicati
2. **Inserisci Spesa** – validazione di data, importo > 0 ed esistenza della categoria
3. **Definisci Budget Mensile** – inserimento o aggiornamento (un budget per mese e categoria)
4. **Visualizza Report** – totale per categoria, spese vs budget, elenco ordinato per data

## Database

Tre tabelle (`categorie`, `spese`, `budget`) con vincoli `PRIMARY KEY`, `FOREIGN KEY`,
`CHECK`, `UNIQUE` e `NOT NULL`, definiti in `sql/database.sql`.
