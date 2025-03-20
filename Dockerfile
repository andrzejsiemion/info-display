# Use a Raspberry Pi-compatible base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install required system packages
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-smbus \
    libgpiod2 \
    i2c-tools \
    && rm -rf /var/lib/apt/lists/*

# Install required Python libraries (RPi.GPIO via pip)
RUN pip install adafruit-circuitpython-ssd1306 pillow adafruit-blinka RPi.GPIO

# Copy the script to the container
COPY oled_display.py /app/oled_display.py

# Set the command to run the script
CMD ["python3", "/app/oled_display.py"]