#!/usr/bin/env bash
# Lance l'application Flask LinkedImmortals.
# Crée le venv, installe les dépendances et construit graph.kuzu si besoin.
# Usage : ./run.sh [port]   (défaut : 5000)
set -euo pipefail

cd "$(dirname "$0")"
PORT="${1:-${PORT:-5000}}"

if [ ! -x .venv/bin/python ]; then
    echo "→ Création de l'environnement virtuel…"
    python3 -m venv .venv
    .venv/bin/pip install -q -r requirements.txt
fi

if [ ! -e graph.kuzu ]; then
    echo "→ Construction de la base graphe (graph.kuzu)…"
    .venv/bin/python build_graph.py
fi

echo "→ http://127.0.0.1:${PORT}"
exec .venv/bin/flask --app app run --port "$PORT"
