FROM python:3.9-slim

# Python-related environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system dependencies needed for compiling package assets (like chromadb)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files (\.dockerignore will exclude .env and other dev artefacts)
COPY . .

# Use the port provided by Hugging Face (default 7860 for local dev)
ARG PORT=7860
ENV PORT=${PORT}
EXPOSE ${PORT}

# Command to run uvicorn, binding to the dynamically injected PORT env variable
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
