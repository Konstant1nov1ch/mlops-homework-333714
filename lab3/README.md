# ЛР3. Портал базы знаний

Портал ищет документы через MCP и формирует ответы со ссылками на источники. Основной маршрут использует llm7, резервный — локальную CPU-модель.

## Локальная проверка

Поместите предоставленный корпус в `corpus.json` или задайте путь через `CORPUS_PATH`.

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt pytest
python validate_corpus.py
python index.py
python evaluate.py
python server.py
```

В другом терминале из того же каталога запустите портал:

```sh
. .venv/bin/activate
uvicorn portal:app --host 127.0.0.1 --port 18084
```

Откройте `http://127.0.0.1:18084`. Подключения настраиваются через `MCP_URL`, `CLOUD_BASE_URL`, `CLOUD_MODEL`, `LLM7_API_KEY`, `LOCAL_BASE_URL` и `LOCAL_MODEL`.

Манифесты Kubernetes находятся в [deploy/](deploy/), результаты проверок — в [отчёте](../reports/ЛР3.md).
