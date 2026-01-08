FROM python:3.10-slim

# Prevents Python from writing .pyc files and buffers
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (psycopg2-binary doesn't need libpq-dev, keep it lean)
RUN pip install --no-cache-dir --upgrade pip

# Install deps first for Docker cache efficiency
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . /app

# Render/Fly/etc will set PORT. Default for local.
ENV PORT=8000

# Start script (runs migrations then launches uvicorn)
CMD ["bash", "start.sh"]
