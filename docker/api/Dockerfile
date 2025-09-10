FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy FastAPI code
COPY ./app ./app

# Expose default port (optional, for documentation)
EXPOSE 8000

# Use shell form CMD so env vars are expanded at runtime
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

