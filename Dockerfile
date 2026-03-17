FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc build-essential

# Copy requirements first
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Copy full project
COPY . .

# Expose port
EXPOSE 10000

# Start app
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "10000"]
