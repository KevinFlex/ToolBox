"""
Interface Streamlit — kevin-toolbox / Module Véhicule Utilitaire
Affiche les annonces récupérées sur AutoScout24, avec filtres et scoring.
"""

import sys
from pathlib import Path

# Ajout du src/ au path pour les imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import streamlit as st
import pandas as pd

from kevin_toolbox.vehicule.scraping import run_searches, MODELS
from kevin_toolbox.vehicule.scoring import score_all
from kevin_toolbox.vehicule.geocoding import enrich_distances
from kevin_toolbox.vehicule.storage import save_all, load_all, count

# ---------------------------------------------------------------------------
# Config page
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="kevin-toolbox — Utilitaire",
    page_icon="🚐",
    layout="wide",
)

st.title("🚐 Recherche véhicule utilitaire")
st.caption("AutoScout24 · Trafic / Jumpy / Expert · Budget ≤ 5 500 € · Montpellier")

# ---------------------------------------------------------------------------
# Sidebar — filtres
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Filtres")

    prix_max = st.slider("Prix max (€)", 1000, 8000, 5500, step=100)
    km_max = st.slider("Kilométrage max", 100_000, 350_000, 220_000, step=10_000)
    score_min = st.slider("Score minimum", 0, 10, 5)

    modeles = st.multiselect(
        "Modèles",
        ["Trafic", "Jumpy", "Expert"],
        default=["Trafic", "Jumpy", "Expert"],
    )

    st.divider()
    if st.button("🔄 Lancer une nouvelle recherche", use_container_width=True):
        with st.spinner("Recherche en cours…"):
            annonces = run_searches()
            annonces = enrich_distances(annonces)
            annonces = score_all(annonces)
            result = save_all(annonces)
            st.success(
                f"{result['new']} nouvelles annonces · {result['updated']} mises à jour"
            )
            if result["new_annonces"]:
                st.info("Nouvelles annonces :")
                for a in result["new_annonces"]:
                    st.write(f"- [{a.title}]({a.url}) — {a.price_eur}€")

# ---------------------------------------------------------------------------
# Chargement des données
# ---------------------------------------------------------------------------
rows = load_all()

if not rows:
    st.info("Aucune annonce en base. Clique sur **Lancer une nouvelle recherche** pour démarrer.")
    st.stop()

df = pd.DataFrame(rows)

# ---------------------------------------------------------------------------
# Filtres appliqués
# ---------------------------------------------------------------------------
mask = (
    (df["price_eur"].fillna(9999) <= prix_max)
    & (df["mileage_km"].fillna(999999) <= km_max)
    & (df["score"].fillna(0) >= score_min)
)

if modeles:
    modeles_lower = [m.lower() for m in modeles]
    mask &= df["title"].str.lower().str.contains("|".join(modeles_lower), na=False)

df_filtered = df[mask].copy()

# ---------------------------------------------------------------------------
# Métriques
# ---------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Annonces affichées", len(df_filtered))
col2.metric("Total en base", count())
col3.metric(
    "Prix moyen",
    f"{int(df_filtered['price_eur'].mean()):,} €".replace(",", " ")
    if not df_filtered.empty else "—"
)
col4.metric(
    "Meilleur score",
    int(df_filtered["score"].max()) if not df_filtered.empty else "—"
)

st.divider()

# ---------------------------------------------------------------------------
# Tableau des annonces
# ---------------------------------------------------------------------------
if df_filtered.empty:
    st.warning("Aucune annonce ne correspond aux filtres.")
else:
    # Colonnes à afficher
    display_cols = ["title", "price_eur", "mileage_km", "city", "distance_km", "score", "url"]
    display_cols = [c for c in display_cols if c in df_filtered.columns]

    df_display = df_filtered[display_cols].rename(columns={
        "title": "Titre",
        "price_eur": "Prix (€)",
        "mileage_km": "Kilométrage",
        "city": "Ville",
        "distance_km": "Distance (km)",
        "score": "Score",
        "url": "Lien",
    })

    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Lien": st.column_config.LinkColumn("Lien", display_text="Voir l'annonce"),
            "Prix (€)": st.column_config.NumberColumn(format="%d €"),
            "Kilométrage": st.column_config.NumberColumn(format="%d km"),
            "Distance (km)": st.column_config.NumberColumn(format="%.0f km"),
            "Score": st.column_config.ProgressColumn(min_value=0, max_value=10),
        },
    )

# ---------------------------------------------------------------------------
# Détail d'une annonce
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Détail d'une annonce")

if not df_filtered.empty:
    choix = st.selectbox(
        "Sélectionner une annonce",
        df_filtered["title"].tolist(),
        index=0,
    )
    row = df_filtered[df_filtered["title"] == choix].iloc[0]

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Titre** : {row.get('title', '—')}")
        st.markdown(f"**Prix** : {row.get('price_eur', '—')} €")
        st.markdown(f"**Kilométrage** : {row.get('mileage_km', '—'):,} km".replace(",", " ") if row.get('mileage_km') else "**Kilométrage** : —")
        st.markdown(f"**Carburant** : {row.get('fuel', '—')}")
        st.markdown(f"**Boîte** : {row.get('gearbox', '—')}")
    with c2:
        st.markdown(f"**Ville** : {row.get('city', '—')}")
        st.markdown(f"**Distance Montpellier** : {row.get('distance_km', '—')} km")
        st.markdown(f"**Score** : {row.get('score', '—')} / 10")
        st.markdown(f"**Première vue** : {row.get('first_seen', '—')[:10] if row.get('first_seen') else '—'}")
        st.markdown(f"[Voir l'annonce sur AutoScout24]({row.get('url', '#')})")
