"""
Interface Streamlit — kevin-toolbox / Module Véhicule Utilitaire
Responsive, avec images, filtres dynamiques lus depuis docs/utilitaire/filtres.md.
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
from kevin_toolbox.core.filters import load_filtres, update_filtre

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
# Sidebar — filtres dynamiques (lus depuis docs/utilitaire/filtres.md)
# ---------------------------------------------------------------------------

def render_sidebar_filtres(filtres: list[dict]) -> dict:
    """
    Génère dynamiquement les widgets Streamlit depuis la liste de filtres.
    Retourne un dict {id: valeur} avec les valeurs saisies.
    """
    values = {}
    for f in filtres:
        if not f.get("actif", True):
            continue
        fid   = f["id"]
        label = f.get("label", fid)
        ftype = f.get("type", "slider")
        desc  = f.get("description", "")

        if ftype == "slider":
            values[fid] = st.slider(
                label,
                min_value=int(f.get("min", 0)),
                max_value=int(f.get("max", 100)),
                value=int(f.get("default", f.get("min", 0))),
                step=int(f.get("step", 1)),
                help=desc,
            )
        elif ftype == "multiselect":
            opts = f.get("options", [])
            values[fid] = st.multiselect(
                label,
                options=opts,
                default=f.get("default", opts),
                help=desc,
            )
        elif ftype == "toggle":
            values[fid] = st.toggle(
                label,
                value=bool(f.get("default", True)),
                help=desc,
            )
    return values


with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/van.png", width=60)
    st.title("Filtres")

    # Chargement des filtres depuis docs/utilitaire/filtres.md
    filtres = load_filtres("utilitaire")
    filtre_values = render_sidebar_filtres(filtres)

    # Récupération des valeurs avec fallback
    prix_max  = filtre_values.get("prix_max", 5500)
    km_max    = filtre_values.get("km_max", 220000)
    dist_max  = filtre_values.get("dist_max", 300)
    score_min = filtre_values.get("score_min", 5)
    modeles   = filtre_values.get("modeles", ["Trafic", "Jumpy", "Expert"])

    vue = st.radio("Affichage", ["Cartes", "Tableau"], horizontal=True)

    # --- Gestion des filtres ---
    st.divider()
    with st.expander("⚙️ Gérer les filtres"):
        st.caption("Active/désactive ou modifie les valeurs par défaut. Sauvegardé dans `docs/utilitaire/filtres.md`.")
        for f in filtres:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{f.get('label', f['id'])}**")
                st.caption(f.get("description", ""))
            with col2:
                actif = st.toggle(
                    "Actif",
                    value=f.get("actif", True),
                    key=f"toggle_{f['id']}",
                )
                if actif != f.get("actif", True):
                    update_filtre("utilitaire", f["id"], actif=actif)
                    st.rerun()

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

# ---------------------------------------------------------------------------
# Page ajout manuel (leboncoin / autre source)
# ---------------------------------------------------------------------------
st.divider()
with st.expander("➕ Ajouter une annonce manuellement (leboncoin, etc.)"):
    st.caption("Colle les infos depuis n'importe quelle annonce — leboncoin, Facebook Marketplace, etc.")

    with st.form("ajout_manuel"):
        col1, col2 = st.columns(2)
        with col1:
            m_titre   = st.text_input("Titre *", placeholder="Ex : Renault Trafic L2H1 2.0 dCi")
            m_prix    = st.number_input("Prix (€)", min_value=0, max_value=50000, value=0, step=100)
            m_km      = st.number_input("Kilométrage", min_value=0, max_value=999999, value=0, step=1000)
            m_annee   = st.number_input("Année", min_value=1990, max_value=2030, value=2010, step=1)
        with col2:
            m_ville   = st.text_input("Ville *", placeholder="Ex : Nîmes")
            m_carbu   = st.selectbox("Carburant", ["Diesel", "Essence", "Électrique", "Hybride", "Autre"])
            m_boite   = st.selectbox("Boîte", ["Manuelle", "Automatique"])
            m_url     = st.text_input("URL de l'annonce *", placeholder="https://www.leboncoin.fr/...")
        m_image   = st.text_input("URL image (optionnel)", placeholder="https://...")
        m_notes   = st.text_area("Notes personnelles", placeholder="CT OK, distribution faite, à voir...")

        submitted = st.form_submit_button("Ajouter à ma base", use_container_width=True)

    if submitted:
        if not m_titre or not m_ville or not m_url:
            st.error("Titre, ville et URL sont obligatoires.")
        else:
            from kevin_toolbox.vehicule.scraping import Annonce
            from kevin_toolbox.vehicule.scoring import score_annonce
            from kevin_toolbox.vehicule.geocoding import distance_from_montpellier
            from kevin_toolbox.vehicule.storage import upsert_annonce, get_conn

            with st.spinner("Calcul de la distance et du score…"):
                dist = distance_from_montpellier(m_ville)

            nouvelle = Annonce(
                url         = m_url,
                source      = "manuel",
                title       = m_titre,
                price_eur   = m_prix or None,
                mileage_km  = m_km or None,
                year        = m_annee or None,
                city        = m_ville,
                fuel        = m_carbu,
                gearbox     = m_boite,
                description = m_notes or None,
                distance_km = dist,
                image_url   = m_image or None,
            )
            nouvelle = score_annonce(nouvelle)
            conn = get_conn()
            upsert_annonce(conn, nouvelle)
            st.success(f"✅ Annonce ajoutée ! Score : {int(nouvelle.score)}/10 · Distance : {dist} km de Montpellier")
            st.rerun()
