# syntax=docker/dockerfile:1
FROM python:3.14.0-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies (needed for Pillow, psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application code
COPY . .

# Collect static files (uses whitenoise in production)
RUN python manage.py collectstatic --noinput

# Create a non-root user with a real home directory 
RUN addgroup --system appgroup && adduser --system --ingroup appgroup --home /home/appuser --create-home appuser
RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && \
                  python manage.py createcachetable && \
                  gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120"]