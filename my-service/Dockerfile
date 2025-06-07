# ---------- Builder Stage ----------
FROM python:3.12-slim AS builder

# Install system dependencies
RUN apt-get update && apt-get install -y curl build-essential

# Install Poetry
ENV POETRY_VERSION=1.8.2
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Set work directory
WORKDIR /app

# Copy only the dependency files
COPY pyproject.toml poetry.lock ./

# Configure Poetry
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Install dependencies
RUN poetry install --only main


# ---------- Final Stage ----------
FROM python:3.12-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy installed site-packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy app source code
COPY . .

# Expose FastAPI port
EXPOSE 9000

# Run app
CMD ["uvicorn", "my_service.main:app", "--host", "0.0.0.0", "--port", "9000"]
