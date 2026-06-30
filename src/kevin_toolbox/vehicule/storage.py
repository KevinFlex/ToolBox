"""
Module véhicule — storage.py
Persistance des annonces dans une base SQLite locale (data/processed/vehicule.db).
Détecte les nouvelles annonces à chaque run (comparaison par URL).
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from .scraping import Annonce

DEFAULT_DB = Path(__file__).resolve().parents[4] / "data" / "processed" / "vehicule.db"


def get_conn(path: Path = DEFAULT_DB) -> sqlite3.Connection:
    """Retourne une connexion SQLite, crée la table si elle n'existe pas."""
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS annonces (
            url          TEXT PRIMARY KEY,
            source       TEXT,
            title        TEXT,
            price_eur    INTEGER,
            mileage_km   INTEGER,
            year         INTEGER,
            city         TEXT,
            distance_km  REAL,
            fuel         TEXT,
            gearbox      TEXT,
            description  TEXT,
            score        REAL,
            first_seen   TEXT,
            last_seen    TEXT
        )
    """)
    conn.commit()
    return conn


def upsert_annonce(conn: sqlite3.Connection, annonce: Annonce) -> bool:
    """
    Insère ou met à jour une annonce.
    Retourne True si c'est une NOUVELLE annonce, False si elle existait déjà.
    """
    now = datetime.now().isoformat()

    # Vérifie si l'annonce existe déjà
    existing = conn.execute(
        "SELECT url FROM annonces WHERE url = ?", (annonce.url,)
    ).fetchone()
    is_new = existing is None

    if is_new:
        conn.execute("""
            INSERT INTO annonces
            (url, source, title, price_eur, mileage_km, year, city,
             distance_km, fuel, gearbox, description, score, first_seen, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            annonce.url, annonce.source, annonce.title, annonce.price_eur,
            annonce.mileage_km, annonce.year, annonce.city, annonce.distance_km,
            annonce.fuel, annonce.gearbox, annonce.description, annonce.score,
            now, now,
        ))
    else:
        # Mise à jour du score, de la distance et du last_seen
        conn.execute("""
            UPDATE annonces
            SET score = ?, distance_km = ?, last_seen = ?
            WHERE url = ?
        """, (annonce.score, annonce.distance_km, now, annonce.url))

    conn.commit()
    return is_new


def save_all(annonces: list[Annonce], path: Path = DEFAULT_DB) -> dict:
    """
    Sauvegarde toutes les annonces.
    Retourne un dict avec le nombre de nouvelles et mises à jour.
    """
    conn = get_conn(path)
    new_count = 0
    updated_count = 0
    new_annonces = []

    for annonce in annonces:
        is_new = upsert_annonce(conn, annonce)
        if is_new:
            new_count += 1
            new_annonces.append(annonce)
        else:
            updated_count += 1

    return {
        "new": new_count,
        "updated": updated_count,
        "new_annonces": new_annonces,
    }


def load_all(path: Path = DEFAULT_DB) -> list[dict]:
    """Retourne toutes les annonces triées par score décroissant."""
    conn = get_conn(path)
    cursor = conn.execute("""
        SELECT url, source, title, price_eur, mileage_km, year,
               city, distance_km, fuel, gearbox, score, first_seen, last_seen
        FROM annonces
        ORDER BY score DESC, price_eur ASC
    """)
    cols = [d[0] for d in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


def load_top(n: int = 10, path: Path = DEFAULT_DB) -> list[dict]:
    """Retourne les n meilleures annonces triées par score décroissant."""
    conn = get_conn(path)
    cursor = conn.execute("""
        SELECT url, source, title, price_eur, mileage_km, year,
               city, distance_km, score, first_seen
        FROM annonces
        ORDER BY score DESC, price_eur ASC
        LIMIT ?
    """, (n,))
    cols = [d[0] for d in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


def count(path: Path = DEFAULT_DB) -> int:
    """Retourne le nombre total d'annonces en base."""
    conn = get_conn(path)
    return conn.execute("SELECT COUNT(*) FROM annonces").fetchone()[0]
