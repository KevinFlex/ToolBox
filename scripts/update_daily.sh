#!/bin/bash
# update_daily.sh — Mise à jour quotidienne kevin-toolbox
# Lancé chaque matin automatiquement.
# Vérifie et met à jour les drivers Playwright pour éviter les ruptures de scraping.

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="$PROJECT_DIR/data/processed/update_daily.log"
mkdir -p "$PROJECT_DIR/data/processed"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== Démarrage mise à jour quotidienne ==="

# --- Mise à jour pip ---
log "Mise à jour pip..."
python -m pip install --upgrade pip --quiet

# --- Mise à jour des dépendances ---
log "Mise à jour des dépendances..."
python -m pip install -r "$PROJECT_DIR/requirements.txt" --upgrade --quiet

# --- Vérification et mise à jour Playwright/Chromium ---
log "Vérification driver Playwright (Chromium)..."
if python -m playwright install chromium 2>&1; then
    log "✅ Driver Playwright OK"
else
    log "❌ ÉCHEC mise à jour driver Playwright"
    # Signal d'échec — sera capté par le cron pour notification
    exit 2
fi

log "=== Mise à jour terminée avec succès ==="
exit 0
