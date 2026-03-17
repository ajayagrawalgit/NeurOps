# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install sushy-tools (Redfish emulator)
RUN pip install --no-cache-dir sushy-tools

# Create directory for emulator data
RUN mkdir -p /app/emulator

# Expose Redfish port
EXPOSE 8000

# Default command to start Redfish emulator
CMD ["sushy-emulator", "--port", "8000", "--fake", "--interface", "0.0.0.0"]