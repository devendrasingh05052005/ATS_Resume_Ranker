#!/usr/bin/env bash
set -euo pipefail

echo "Python version:" $(python --version)

pip install --upgrade pip
pip install -r requirements-render.txt

python - <<'PY'
import nltk
nltk.download('stopwords', quiet=True)
print("NLTK stopwords downloaded")
PY

python manage.py migrate --noinput
python manage.py collectstatic --noinput
