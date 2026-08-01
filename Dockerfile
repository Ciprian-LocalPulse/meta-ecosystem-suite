FROM python:3.14-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY meta_ecosystem_suite ./meta_ecosystem_suite

RUN pip install --no-cache-dir .

COPY . .

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["meta-suite"]
CMD ["--help"]
