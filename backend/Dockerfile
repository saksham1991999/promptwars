FROM python:3.12-slim

WORKDIR /app

# Install dependencies from requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

# Explicitly listen on 8080 (Cloud Run default)
ENV PORT=8080
ENV ENVIRONMENT=production
ENV LOG_LEVEL=INFO

# Command to run uvicorn on the port provided by Cloud Run
CMD uvicorn app.main:app --host 0.0.0.0 --port 8080
