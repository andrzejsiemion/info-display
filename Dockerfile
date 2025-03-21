# Stage 1: Build dependencies
FROM python:3.11 AS builder

# Set working directory
WORKDIR /app

# Install required Python libraries (including lgpio via pip)
RUN pip install --upgrade pip \
    && pip install adafruit-circuitpython-ssd1306 pillow adafruit-blinka RPi.GPIO lgpio influxdb-client pytz loguru

# Stage 2: Final minimal image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install required system dependencies (without python3-lgpio)
RUN apt-get update && apt-get install -y \
    python3-smbus \
    libgpiod2 \
    i2c-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy only necessary files from builder stage
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11

# Copy script into container
COPY oled_display.py /app/oled_display.py

RUN mkdir -p /app/display

COPY up.txt /app/display/up.txt
COPY down.txt /app/display/down.txt

# Set the command to run the script
CMD ["python3", "/app/oled_display.py"]