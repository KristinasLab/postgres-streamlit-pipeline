FROM python:3.11-slim

# Set working directory for the ETL code
WORKDIR /app

# Copy Python dependencies and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ETL script
COPY load_data.py .

# Run ETL script
CMD ["python", "load_data.py"]

