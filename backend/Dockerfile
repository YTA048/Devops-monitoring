# ---------- STAGE 1: build ----------
FROM python:3.10-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ---------- STAGE 2: runtime ----------
FROM python:3.10-slim

WORKDIR /app

# user non-root
RUN useradd -m appuser

# copy only needed files
COPY --from=builder /root/.local /home/appuser/.local
COPY . .

ENV PATH=/home/appuser/.local/bin:

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
