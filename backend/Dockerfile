FROM python:3.13-slim

COPY --from=hashicorp/terraform:1.10 /bin/terraform /usr/local/bin/terraform

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY pyproject.toml .
RUN pip install .

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 8000

# Command to run the application with hot reload
CMD ["uvicorn", "src.api:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]