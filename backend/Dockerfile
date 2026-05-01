# syntax=docker/dockerfile:1.6
###############################################################################
# Stage 1 — builder : installation des dépendances dans un venv
###############################################################################
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Dépendances système nécessaires à la compilation de psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Création d'un venv isolé
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

###############################################################################
# Stage 2 — runtime : image minimale, user non-root
###############################################################################
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# libpq runtime + curl pour healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 curl \
    && rm -rf /var/lib/apt/lists/*

# Utilisateur non-root
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# Copie du venv depuis le builder
COPY --from=builder /opt/venv /opt/venv

# Copie du code applicatif
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
