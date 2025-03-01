# Please fill in Dockerfile content

# Use an official Python image
FROM python:3.12

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies from pyproject.toml
RUN pip install --no-cache-dir .

# Expose the FastAPI port
EXPOSE 9000

# Run FastAPI
CMD ["uvicorn", "my_service.main:app", "--host", "0.0.0.0", "--port", "9000"]
