FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (build-essential for some python packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Default entrypoint (allows passing arguments)
ENTRYPOINT ["python", "main.py"]
CMD ["--help"]
