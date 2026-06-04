# Droidify — Hugging Face Spaces Dockerfile
# Single container: FastAPI serves static frontend + all /api/* routes on port 7860

FROM python:3.12-alpine AS builder
WORKDIR /build
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-alpine

RUN adduser -D -u 1000 -g "" user

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PORT=7860 \
    CACHE_DEFAULT_TTL=300 \
    STATIC_DIR=/home/user/app/frontend

WORKDIR /home/user/app

COPY --from=builder /usr/local/lib/python3.12/site-packages \
                    /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# BUILD_INFO changes on every push — busts all subsequent COPY layers
COPY --chown=user:user BUILD_INFO  ./BUILD_INFO
COPY --chown=user:user backend/app  ./app
COPY --chown=user:user frontend     ./frontend

# Bust service worker and HTML asset cache on every build.
# date +%s gives a unique timestamp each time docker build runs.
# HF rebuilds the image on every push so users always get fresh files.
RUN BUILD_V=$(date +%s) && \
    echo "[cache-bust] v=${BUILD_V}" && \
    sed -i "s/droidify-v[0-9]*/droidify-v${BUILD_V}/g" ./frontend/sw.js && \
    find ./frontend -name "*.html" -exec \
        sed -i "s/?v=[0-9]*/?v=${BUILD_V}/g" {} \;

USER user
EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=5 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:7860/api/health', timeout=8)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]
