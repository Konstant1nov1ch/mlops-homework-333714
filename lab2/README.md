# ЛР2. Runbook Search API

Поиск по инженерным инструкциям на гибридном TF-IDF. Индекс собирается в Docker-образ; Helm и GitHub Actions обеспечивают выпуск в staging и production с проверкой качества и откатом.

## Запуск и проверка

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python scripts/build_index.py
pytest -q
python scripts/evaluate.py
python scripts/evaluate.py --ranking-mode reverse  # проверка должна не пройти
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

В другом терминале: `python smoke.py http://127.0.0.1:8000`.

Основные маршруты: `POST /v1/search`, `GET /v1/documents/{id}/recommendations`, `/livez`, `/readyz`, `/meta`, `/metrics` и `/docs`.

[Pipeline выпуска](https://github.com/Konstant1nov1ch/mlops-homework-333714/actions/runs/45609995917) · [Отчёт](../reports/ЛР2.md)
