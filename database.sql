-- ============================================================
-- SISTEMA DI GESTIONE DELLE SPESE PERSONALI E DEL BUDGET
-- Script SQL (SQLite) - creazione schema + dati di esempio
-- ============================================================

PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------
-- a) CREAZIONE DEL DATABASE
-- ------------------------------------------------------------

DROP TABLE IF EXISTS budget;
DROP TABLE IF EXISTS spese;
DROP TABLE IF EXISTS categorie;

-- Tabella delle categorie di spesa
CREATE TABLE categorie (
    id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,          -- PRIMARY KEY
    nome         TEXT NOT NULL UNIQUE COLLATE NOCASE         -- NOT NULL + UNIQUE
                 CHECK (length(trim(nome)) > 0)              -- CHECK: nome non vuoto
);

-- Tabella delle spese
CREATE TABLE spese (
    id_spesa     INTEGER PRIMARY KEY AUTOINCREMENT,          -- PRIMARY KEY
    data         TEXT    NOT NULL                            -- NOT NULL
                 CHECK (data GLOB '[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]'),
    importo      REAL    NOT NULL
                 CHECK (importo > 0),                        -- CHECK: importo > 0
    id_categoria INTEGER NOT NULL,
    descrizione  TEXT,                                       -- facoltativa
    FOREIGN KEY (id_categoria)                               -- FOREIGN KEY
        REFERENCES categorie (id_categoria)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- Tabella dei budget mensili (uno per categoria e per mese)
CREATE TABLE budget (
    id_budget      INTEGER PRIMARY KEY AUTOINCREMENT,        -- PRIMARY KEY
    mese           TEXT    NOT NULL                          -- formato YYYY-MM
                   CHECK (mese GLOB '[0-9][0-9][0-9][0-9]-[0-1][0-9]'),
    id_categoria   INTEGER NOT NULL,
    importo_budget REAL    NOT NULL
                   CHECK (importo_budget > 0),               -- CHECK: budget > 0
    FOREIGN KEY (id_categoria)                               -- FOREIGN KEY
        REFERENCES categorie (id_categoria)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    UNIQUE (mese, id_categoria)                              -- UNIQUE composto
);

-- ==== DATI DI ESEMPIO ====
-- ------------------------------------------------------------
-- b) INSERIMENTO DATI DI ESEMPIO
-- ------------------------------------------------------------

INSERT INTO categorie (nome) VALUES
    ('Alimentari'),
    ('Trasporti'),
    ('Svago'),
    ('Salute');

INSERT INTO spese (data, importo, id_categoria, descrizione) VALUES
    ('2025-01-03', 45.50,  1, 'Spesa settimanale'),
    ('2025-01-10', 120.00, 1, 'Cena con amici'),
    ('2025-01-15', 25.00,  1, 'Pranzo'),
    ('2025-01-20', 130.00, 1, 'Spesa supermercato'),
    ('2025-01-05', 60.00,  2, 'Abbonamento autobus'),
    ('2025-01-18', 60.00,  2, 'Benzina'),
    ('2025-01-25', 35.00,  3, 'Cinema e popcorn'),
    ('2025-02-02', 80.00,  1, 'Spesa settimanale'),
    ('2025-02-14', 90.00,  3, 'Cena di San Valentino'),
    ('2025-02-20', 40.00,  4, 'Visita medica');

INSERT INTO budget (mese, id_categoria, importo_budget) VALUES
    ('2025-01', 1, 300.00),   -- Alimentari: sforato (320.50 > 300)
    ('2025-01', 2, 150.00),   -- Trasporti: nel budget (120 <= 150)
    ('2025-01', 3, 100.00),   -- Svago: nel budget (35 <= 100)
    ('2025-02', 1, 250.00),   -- Alimentari: nel budget (80 <= 250)
    ('2025-02', 3, 80.00);    -- Svago: sforato (90 > 80)

-- ------------------------------------------------------------
-- c) QUERY USATE DAI REPORT (come commento, a titolo di esempio)
-- ------------------------------------------------------------

-- Report 1: totale spese per categoria
-- SELECT c.nome, SUM(s.importo) AS totale
-- FROM categorie c JOIN spese s ON s.id_categoria = c.id_categoria
-- GROUP BY c.id_categoria ORDER BY totale DESC;

-- Report 2: spese mensili vs budget
-- SELECT b.mese, c.nome, b.importo_budget, COALESCE(SUM(s.importo),0) AS speso
-- FROM budget b
-- JOIN categorie c ON c.id_categoria = b.id_categoria
-- LEFT JOIN spese s ON s.id_categoria = b.id_categoria
--                  AND substr(s.data,1,7) = b.mese
-- GROUP BY b.id_budget ORDER BY b.mese, c.nome;

-- Report 3: elenco completo ordinato per data
-- SELECT s.data, c.nome, s.importo, COALESCE(s.descrizione,'')
-- FROM spese s JOIN categorie c ON c.id_categoria = s.id_categoria
-- ORDER BY s.data, s.id_spesa;
