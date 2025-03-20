# Use Raspberry Pi OS-based Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install required system packages
RUN apt-get update && apt-get install -y \
    python3-pip \
    libgpiod2 \
    i2c-tools \
    && rm -rf /var/lib/apt/lists/*

# Install required Python libraries
RUN pip install adafruit-circuitpython-ssd1306 pillow

# Copy the script to the container
COPY oled_display.py /app/oled_display.py

# Set the command to run the script
CMD ["python3", "/app/oled_display.py"]
