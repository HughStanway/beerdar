# Stage 1: Build Dependencies
FROM python:3.11-slim AS builder
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime Container
FROM python:3.11-slim AS runner
WORKDIR /app
COPY --from=builder /install /usr/local
COPY backend/ .
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
