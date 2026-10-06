# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
RUN groupadd --system app && useradd --system --gid app --home-dir /app app
WORKDIR /app/backend
COPY backend/pyproject.toml ./

FROM base AS dev
# Install deps only (source is bind-mounted in development).
RUN pip install --upgrade pip && \
    python -c "import tomllib;d=tomllib.load(open('pyproject.toml','rb'))['project'];print('\n'.join(d['dependencies']+d['optional-dependencies']['dev']))" > /tmp/req.txt && \
    pip install -r /tmp/req.txt
USER app
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]

FROM base AS prod
COPY backend/ ./
RUN pip install . && chown -R app:app /app
USER app
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers"]
