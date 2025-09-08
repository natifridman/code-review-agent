# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set labels for metadata
LABEL maintainer="Code Review Agent"
LABEL description="AI-powered code review using CrewAI and Gemini API"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Create necessary directories
RUN mkdir -p /github/workspace

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Make main script executable
RUN chmod +x src/main.py

# Set default working directory for the action
WORKDIR /github/workspace

# Run the main script
ENTRYPOINT ["python", "/app/src/main.py"]