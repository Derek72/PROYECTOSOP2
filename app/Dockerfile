# ETAPA 1: Build
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ETAPA 2: Final
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH

EXPOSE 5000

# Gunicorn maneja SIGTERM automáticamente
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "main:app"]