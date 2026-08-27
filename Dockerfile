# syntax=docker/dockerfile:1

FROM python:3.13-slim

# Prevent Python from writing .pyc files and enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System dependencies required by opencv-python-headless, tensorflow and
# related ML libraries (mtcnn, retina-face, keras-facenet)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxcb1 \
    libx11-6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libsm6 \
    libxcb-render0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# .env files, if present, are copied along with the app code above and are
# read at runtime via python-dotenv (see app/config.py). No virtualenv is
# used inside the container since dependencies are installed system-wide.

EXPOSE 8000

# No CMD instruction here: Railway's startCommand (configured in railway.json
# or the service settings) controls how the container starts. A Dockerfile
# CMD would otherwise take precedence over Railway's startCommand.

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]