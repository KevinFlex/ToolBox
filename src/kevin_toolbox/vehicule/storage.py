"""
Module véhicule — storage.py
Persistance des annonces dans une base SQLite locale (data/processed/vehicule.db).
"""

import sqlite3
from pathlib import Path
from .scraping import Annonce

DEFAULT_DB = Path(__file__).resolve().parents[4] / "data" / "processed" / "vehicule.db"


def get_conn(path: Path = DEFAULT_DB) -> sqlite3.Connection:
    """Retourne une connexion SQLite, crée la table si elle n'existe pas."""
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS annonces (
            url         TEXT PRIMARY KEY,
            source      TEXT,
            title       TEXT,
            price_eur   INTEGER,
            mileage_km  INTEGER,
            year        INTEGER,
            city        TEXT,
            distance_km REAL,
            fuel        TEXT,
            gearbox     TEXT,
            description TEXT,
            score       REAL
        )
    """)
    conn.commit()
    return conn


def upsert_annonce(conn: sqlite3.Connection, annonce: Annonce) -> None:
    """Insère ou met à jour une annonce dans la base."""
    conn.execute("""
        INSERT OR REPLACE INTO annonces
        (url, source, title, price_eur, mileage_km, year, city,
         distance_km, fuel, gearbox, description, score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        annonce.url, annonce.source, annonce.title, annonce.price_eur,
        annonce.mileage_km, annonce.year, annonce.city, annonce.distance_km,
        annonce.fuel, annonce.gearbox, annonce.description, annonce.score,
    ))
    conn.commit()


def save_all(annonces: list[Annonce], path: Path = DEFAULT_DB) -> int:
    """Sauvegarde toutes les annonces. Retourne le nombre de lignes insérées/mises à jour."""
    conn = get_conn(path)
    for annonce in annonces:
        upsert_annonce(conn, annonce)
    return len(annonces)


def load_top(n: int = 10, path: Path = DEFAULT_DB) -> list[dict]:
    """Retourne les n meilleures annonces triées par score décroissant."""
    conn = get_conn(path)
    cursor = conn.execute("""
        SELECT url, source, title, price_eur, mileage_km, year, city, score
        FROM annonces
        ORDER BY score DESC
        LIMIT ?
    """, (n,))
    cols = [d[0] for d in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]
