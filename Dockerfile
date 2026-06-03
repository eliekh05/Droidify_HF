# Droidify — Hugging Face Spaces Dockerfile
# Single container: FastAPI serves static frontend + all /api/* routes on port 7860
# Main repo (self-hosted): github.com/eliekh05/Droidify — uses nginx + FastAPI, port 80

FROM python:3.12-alpine AS builder
WORKDIR /build
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-alpine

# HF Spaces requires UID 1000
RUN adduser -D -u 1000 -g "" user

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PORT=7860 \
    CACHE_DEFAULT_TTL=300 \
    STATIC_DIR=/home/user/app/frontend

WORKDIR /home/user/app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages \
                    /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy app code and frontend
COPY --chown=user:user backend/app     ./app
COPY --chown=user:user frontend ./frontend

USER user
EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=5 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:7860/api/health', timeout=8)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]
