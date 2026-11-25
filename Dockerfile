# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final runner stage
FROM python:3.11-slim AS runner

WORKDIR /app

# Crear usuario sin privilegios para estandares de seguridad en produccion
RUN useradd -m -u 1000 appuser

# Copiar librerias compiladas desde el builder
COPY --from=builder /root/.local /home/appuser/.local

# Copiar codigo fuente del proyecto
COPY services ./services
COPY data ./data
COPY models ./models
COPY tests ./tests
COPY README.md .

ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PORT=8000

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request, os; port=os.environ.get('PORT','8000'); urllib.request.urlopen(f'http://127.0.0.1:{port}/').getcode() == 200 or exit(1)"

CMD ["sh", "-c", "python -m uvicorn services.web.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
