# ---------- Builder Stage ----------
FROM python:3.12-slim AS builder

# Install system dependencies
RUN apt-get update && apt-get install -y curl build-essential

# Install Poetry
ENV POETRY_VERSION=1.8.2
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Set work directory
WORKDIR /app

# Copy only the dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry export --without-hashes --only main -f requirements.txt > requirements.txt

# ---------- Final Stage ----------
FROM python:3.12-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements from builder
COPY --from=builder /app/requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source code
COPY . .

# Expose FastAPI port
EXPOSE 9000

# Run app
CMD ["uvicorn", "my_service.main:app", "--host", "0.0.0.0", "--port", "9000"]
