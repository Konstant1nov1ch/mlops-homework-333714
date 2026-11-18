FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY index.py validate_corpus.py kb.py server.py portal.py safety.py relay.py ./
USER 10001:10001
EXPOSE 8000
CMD ["python", "server.py"]
