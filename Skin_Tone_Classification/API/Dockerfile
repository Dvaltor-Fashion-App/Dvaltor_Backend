# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.11.3
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install OpenCV, FFmpeg and system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code and folders
COPY Models /app/Models
COPY Dataset /app/Dataset
COPY . .

# Expose the port
EXPOSE 8080

# Start the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
# --- Dockerfile for Skin Tone Classification API ---
# This Dockerfile sets up a Python environment with necessary dependencies for the Skin Tone Classification API.