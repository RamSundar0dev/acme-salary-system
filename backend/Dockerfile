FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for postgres and healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && python -m app.scripts.bootstrap_admin && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
