FROM python:3.11-slim AS build
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY data ./data
COPY scripts ./scripts
RUN python scripts/build_index.py && python scripts/evaluate.py

FROM python:3.11-slim
WORKDIR /app
COPY --from=build /usr/local /usr/local
COPY --from=build /app/app ./app
COPY --from=build /app/artifacts ./artifacts
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
