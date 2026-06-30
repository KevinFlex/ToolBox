"""
Interface Streamlit — kevin-toolbox / Module Véhicule Utilitaire
Responsive, avec images, filtres paramétrables dont distance Montpellier.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import streamlit as st
import pandas as pd

from kevin_toolbox.vehicule.scraping import run_searches
from kevin_toolbox.vehicule.scoring import score_all
from kevin_toolbox.vehicule.geocoding import enrich_distances
from kevin_toolbox.vehicule.storage import save_all, load_all, count

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="ToolBox — Utilitaire",
    page_icon="🚐",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* Responsive cards */
.annonce-card {
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 16px;
    background: #fafafa;
}
.annonce-card img {
    width: 100%;
    border-radius: 8px;
    object-fit: cover;
    max-height: 180px;
}
.annonce-title {
    font-weight: 600;
    font-size: 0.95rem;
    margin: 8px 0 4px 0;
    line-height: 1.3;
}
.annonce-meta {
    font-size: 0.82rem;
    color: #555;
    margin: 2px 0;
}
.annonce-price {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1a6e3c;
    margin: 6px 0;
}
.badge {
    display: inline-block;
    background: #eef2ff;
    color: #3730a3;
    border-radius: 6px;
    padding: 2px 8px;
    font-size: 0.75rem;
    margin-right: 4px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar — filtres
# ---------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/van.png", width=60)
    st.title("Filtres")

    prix_max = st.slider("Prix max (€)", 500, 8000, 5500, step=100)
    km_max = st.slider("Kilométrage max (km)", 50_000, 350_000, 220_000, step=10_000)
    dist_max = st.slider("Distance max de Montpellier (km)", 50, 800, 300, step=25)
    score_min = st.slider("Score minimum", 0, 10, 5)

    modeles = st.multiselect(
        "Modèles",
        ["Trafic", "Jumpy", "Expert"],
        default=["Trafic", "Jumpy", "Expert"],
    )

    vue = st.radio("Affichage", ["Cartes", "Tableau"], horizontal=True)

    st.divider()

    if st.button("🔄 Nouvelle recherche", use_container_width=True):
        with st.spinner("Recherche en cours…"):
            annonces = run_searches()
            annonces = enrich_distances(annonces)
            annonces = score_all(annonces)
            result = save_all(annonces)
        if result["new"] > 0:
            st.success(f"✅ {result['new']} nouvelles annonces !")
            for a in result["new_annonces"]:
                st.write(f"- [{a.title}]({a.url})")
        else:
            st.info("Aucune nouvelle annonce.")

# ---------------------------------------------------------------------------
# Chargement
# ---------------------------------------------------------------------------
rows = load_all()

if not rows:
    st.title("🚐 Recherche véhicule utilitaire")
    st.info("Aucune annonce en base. Clique sur **Nouvelle recherche** dans la barre latérale.")
    st.stop()

df = pd.DataFrame(rows)

# ---------------------------------------------------------------------------
# Filtres
# ---------------------------------------------------------------------------
mask = (
    (df["price_eur"].fillna(9999) <= prix_max)
    & (df["mileage_km"].fillna(999_999) <= km_max)
    & (df["score"].fillna(0) >= score_min)
    & (df["distance_km"].fillna(0) <= dist_max)
)
if modeles:
    mask &= df["title"].str.lower().str.contains(
        "|".join(m.lower() for m in modeles), na=False
    )

df_f = df[mask].copy().reset_index(drop=True)

# ---------------------------------------------------------------------------
# Header + métriques
# ---------------------------------------------------------------------------
st.title("🚐 Véhicule utilitaire")
st.caption("AutoScout24 · Trafic / Jumpy / Expert · Budget ≤ 5 500 € · Montpellier")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Annonces affichées", len(df_f))
c2.metric("Total en base", count())
c3.metric(
    "Prix moyen",
    f"{int(df_f['price_eur'].mean()):,} €".replace(",", " ") if not df_f.empty else "—"
)
c4.metric(
    "Distance moy.",
    f"{int(df_f['distance_km'].mean())} km" if not df_f.empty and df_f['distance_km'].notna().any() else "—"
)

st.divider()

if df_f.empty:
    st.warning("Aucune annonce ne correspond aux filtres.")
    st.stop()

# ---------------------------------------------------------------------------
# Vue Cartes
# ---------------------------------------------------------------------------
if vue == "Cartes":
    cols_per_row = 3
    rows_data = [df_f.iloc[i:i+cols_per_row] for i in range(0, len(df_f), cols_per_row)]

    for row_group in rows_data:
        cols = st.columns(cols_per_row)
        for col, (_, a) in zip(cols, row_group.iterrows()):
            with col:
                # Image
                img = a.get("image_url")
                if img:
                    st.image(img, use_container_width=True)
                else:
                    st.image("https://img.icons8.com/fluency/200/van.png", use_container_width=True)

                # Titre
                st.markdown(f"**{a['title']}**")

                # Prix + score
                prix = f"{int(a['price_eur'])} €" if a.get("price_eur") else "N/A"
                score = int(a["score"]) if a.get("score") else 0
                st.markdown(f"### {prix} &nbsp; `{score}/10`", unsafe_allow_html=True)

                # Métadonnées
                km = f"{int(a['mileage_km']):,} km".replace(",", " ") if a.get("mileage_km") else "—"
                dist = f"{int(a['distance_km'])} km de Montpellier" if a.get("distance_km") else "—"
                fuel = a.get("fuel") or "—"
                city = a.get("city") or "—"

                st.caption(f"🛣 {km} · ⛽ {fuel}")
                st.caption(f"📍 {city} · {dist}")

                st.link_button("Voir l'annonce", a["url"], use_container_width=True)
                st.divider()

# ---------------------------------------------------------------------------
# Vue Tableau
# ---------------------------------------------------------------------------
else:
    display_cols = ["title", "price_eur", "mileage_km", "city", "distance_km", "score", "url"]
    display_cols = [c for c in display_cols if c in df_f.columns]

    st.dataframe(
        df_f[display_cols].rename(columns={
            "title": "Titre",
            "price_eur": "Prix (€)",
            "mileage_km": "Kilométrage",
            "city": "Ville",
            "distance_km": "Distance (km)",
            "score": "Score",
            "url": "Lien",
        }),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Lien": st.column_config.LinkColumn("Lien", display_text="Voir"),
            "Prix (€)": st.column_config.NumberColumn(format="%d €"),
            "Kilométrage": st.column_config.NumberColumn(format="%d km"),
            "Distance (km)": st.column_config.NumberColumn(format="%.0f km"),
            "Score": st.column_config.ProgressColumn(min_value=0, max_value=10),
        },
    )

# ---------------------------------------------------------------------------
# Détail annonce (vue tableau uniquement)
# ---------------------------------------------------------------------------
if vue == "Tableau":
    st.divider()
    st.subheader("Détail")
    choix = st.selectbox("Sélectionner", df_f["title"].tolist())
    row = df_f[df_f["title"] == choix].iloc[0]

    col_img, col_info = st.columns([1, 2])
    with col_img:
        img = row.get("image_url")
        if img:
            st.image(img, use_container_width=True)
        else:
            st.image("https://img.icons8.com/fluency/200/van.png", use_container_width=True)

    with col_info:
        st.markdown(f"### {row.get('title', '—')}")
        st.markdown(f"**Prix** : {row.get('price_eur', '—')} €")
        km = f"{int(row['mileage_km']):,} km".replace(",", " ") if row.get('mileage_km') else "—"
        st.markdown(f"**Kilométrage** : {km}")
        st.markdown(f"**Carburant** : {row.get('fuel', '—')}")
        st.markdown(f"**Boîte** : {row.get('gearbox', '—')}")
        st.markdown(f"**Ville** : {row.get('city', '—')}")
        dist = f"{int(row['distance_km'])} km" if row.get('distance_km') else "—"
        st.markdown(f"**Distance Montpellier** : {dist}")
        st.markdown(f"**Score** : {int(row.get('score', 0))} / 10")
        st.link_button("Voir l'annonce sur AutoScout24", row.get("url", "#"), use_container_width=True)
