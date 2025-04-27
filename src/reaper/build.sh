#!/usr/bin/env bash
# exit on error
set -o errexit
set -o nounset
set -o pipefail

# Mise à jour de pip
echo "Updating pip..."
python -m pip install --upgrade pip

# Installation des dépendances
echo "Installing dependencies..."
pip install -r requirements.txt

# Collecte des fichiers statiques (en mode production)
echo "Collecting static files..."
DJANGO_SETTINGS_MODULE=core.settings.production python manage.py collectstatic --no-input

# Exécution des migrations
echo "Applying database migrations..."
python manage.py migrate

echo "Build process completed successfully."
