# ЛР1. Классификация Iris

FastAPI-сервис с моделью Random Forest. Образ опубликован в [Docker Hub](https://hub.docker.com/r/kostyapin/iris-333714); манифест — [kubernetes.yaml](kubernetes.yaml).

## Запуск

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python train.py
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

В другом терминале:

```sh
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{"features":[5.1,3.5,1.4,0.2]}'
```

Ожидаемый класс — `0`. Результаты проверки в кластере приведены в [отчёте](../reports/ЛР1.md).
