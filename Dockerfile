FROM python:3.11-slim-buster

WORKDIR /app

COPY pyproject.toml README.md ./  # Copy pyproject.toml and README.md

# Install build dependencies and then the package itself
RUN pip install --no-cache-dir hatchling && \
    pip install --no-cache-dir -e .

COPY . .

# Assuming the CLI entrypoint is defined in pyproject.toml as meta-suite
ENTRYPOINT ["meta-suite"]
