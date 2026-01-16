# Use NVIDIA CUDA base image
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# Set non-interactive mode for apt
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies
# python3, python3-pip, git are required
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Alias python to python3
RUN ln -s /usr/bin/python3 /usr/bin/python

# Install Python dependencies
COPY requirements.txt .
# Ensure torch detects CUDA appropriately (pip usually handles this if CUDA is present on host but safe to be explicit sometimes)
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Default entrypoint
ENTRYPOINT ["python", "main.py"]
CMD ["--help"]
