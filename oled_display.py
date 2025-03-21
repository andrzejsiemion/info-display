import time
import os
import board
import busio
import signal
import sys
import socket
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
from influxdb_client import InfluxDBClient

# === OLED Setup ===
WIDTH = 128
HEIGHT = 64
i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c)
font = ImageFont.load_default()

def clear_display():
    oled.fill(0)
    oled.show()

def signal_handler(sig, frame):
    print("Stopping. Clearing display.")
    clear_display()
    sys.exit(0)

# Handle termination signals
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# === InfluxDB Config from Environment ===
INFLUX_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUXDB_TOKEN", "")
ORG = os.getenv("INFLUXDB_ORG", "")
BUCKET = os.getenv("INFLUXDB_BUCKET", "")
MEASUREMENT = os.getenv("INFLUXDB_MEASUREMENT", "")
FIELD = os.getenv("INFLUXDB_FIELD", "")
SENSOR_ID = os.getenv("INFLUXDB_SENSOR_ID", "")

# === InfluxDB Client ===
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
query_api = client.query_api()

# === Main Loop ===
from datetime import datetime

# Main loop
while True:
    try:
        result = query_api.query(org=ORG, query=query)
        if result and len(result[0].records) > 0:
            record = result[0].records[0]
            humidity = record.get_value()
            timestamp = record.get_time().astimezone().strftime("%Y-%m-%d %H:%M:%S")
            sensor_id = record.values.get("sensor_id", "unknown")

            line1 = f"{timestamp} {sensor_id}"
            line2 = f"Hum: {humidity:.1f}%"
        else:
            line1 = "No data"
            line2 = ""
    except Exception as e:
        print(f"InfluxDB error: {e}")
        line1 = "Influx error"
        line2 = ""

    # Create image buffer
    image = Image.new("1", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)

    # Draw text lines
    draw.text((0, 15), line1, font=font, fill=255)
    draw.text((0, 35), line2, font=font, fill=255)

    # Update display
    oled.image(image)
    oled.show()

    time.sleep(60)