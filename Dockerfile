FROM python:3.11-slim

# Install system dependencies (remove curl if not needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for Docker build caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files (including .lib/)
COPY . .

# Expose Flask port
EXPOSE 5000

# Run Flask app
CMD ["python", "web.py"]
