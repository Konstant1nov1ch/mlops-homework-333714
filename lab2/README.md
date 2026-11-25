# ЛР2: выпуск Runbook Search API

Сервис сохраняет учебный API `/v1/search`, рекомендации `/v1/documents/{id}/recommendations`, проверки `/livez`, `/readyz`, `/meta` и `/metrics`. Индекс гибридного TF-IDF собирается из 12 исходных документов и попадает в образ при сборке. Режим `reverse` используется для проверки обнаружения деградации.

## Происхождение основы

Исходное приложение, обучающие документы, контрольный набор, скрипты индексации и тесты восстановлены из общей учебной основы: их Git blob-хеши совпали в начальных состояниях нескольких независимых студенческих репозиториев. Для проверки происхождения использованы [зафиксированная версия одного репозитория](https://gitlab.com/mlops7334048/lab2/-/tree/6936c47d2b5d) и [ранняя версия другого](https://github.com/lesaaly/mlops-search/tree/1a264a49d5f874b9a83f5f27d342a57f1072d62e). Официальный источник раздачи не установлен. Настройки контейнера, Helm, semantic smoke и pipeline адаптированы самостоятельно к этой основе; в `/meta` добавлены хеш корпуса и режим ранжирования для сверки релиза.

## Проверка

```sh
pip install -r requirements.txt
python scripts/build_index.py
pytest -q
python scripts/evaluate.py
python scripts/evaluate.py --ranking-mode reverse  # ожидается ошибка качества
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

В другом терминале: `python smoke.py http://127.0.0.1:8000`. В Helm требуется `image.digest`; staging и production получают один digest. Ручной workflow `retrieval release` с параметром `deploy` выполняет staging, требует подтверждения production, проверяет reverse и откат.
