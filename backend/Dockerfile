FROM python:3.12-slim

WORKDIR /app

# Install only the deps we actually use (no supabase, no pydantic-ai)
RUN pip install --no-cache-dir \
    fastapi==0.129.0 \
    uvicorn[standard]==0.40.0 \
    python-chess==1.999 \
    pydantic==2.12.5 \
    pydantic-settings==2.13.0

COPY ./app ./app

# Cloud Run injects PORT env var
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
