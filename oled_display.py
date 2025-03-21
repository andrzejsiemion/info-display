import os
import time
import signal
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

import board
import busio
import adafruit_ssd1306

from influxdb_client import InfluxDBClient

# === OLED Display Setup ===
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

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# === InfluxDB Config from Environment ===
INFLUX_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUXDB_TOKEN", "")
ORG = os.getenv("INFLUXDB_ORG", "")
BUCKET = os.getenv("INFLUXDB_BUCKET", "")
MEASUREMENT = os.getenv("INFLUXDB_MEASUREMENT", "")
SENSOR_ID = os.getenv("INFLUXDB_SENSOR_ID1", "")

FIELD_HUMIDITY = os.getenv("INFLUXDB_FIELD_HUMIDITY", "humidity")
FIELD_TEMPERATURE = os.getenv("INFLUXDB_FIELD_TEMPERATURE", "temperature")

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
query_api = client.query_api()

def build_query(field):
    return f'''
from(bucket: "{BUCKET}")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "{MEASUREMENT}")
  |> filter(fn: (r) => r._field == "{field}")
  |> filter(fn: (r) => r.sensor_id == "{SENSOR_ID}")
  |> last()
'''

query_temp = build_query(FIELD_TEMPERATURE)
query_hum = build_query(FIELD_HUMIDITY)

# === Main Loop ===
while True:
    try:
        temp_val, hum_val, timestamp = None, None, None

        # Fetch temperature
        temp_result = query_api.query(org=ORG, query=query_temp)
        if temp_result and len(temp_result[0].records) > 0:
            record = temp_result[0].records[0]
            temp_val = record.get_value()
            timestamp = record.get_time().astimezone().strftime("%y-%m-%d %H:%M")
            sensor_id = record.values.get("sensor_id", "unknown")

        # Fetch humidity
        hum_result = query_api.query(org=ORG, query=query_hum)
        if hum_result and len(hum_result[0].records) > 0:
            record = hum_result[0].records[0]
            hum_val = record.get_value()

        if temp_val is not None and hum_val is not None:
            line1 = f"{timestamp} {sensor_id}"
            line2 = f"Temp: {temp_val:.1f}°C  Hum: {hum_val:.1f}%"
        else:
            line1 = "No data"
            line2 = ""

    except Exception as e:
        print(f"InfluxDB error: {e}")
        line1 = "Influx error"
        line2 = ""

    # Draw to OLED
    image = Image.new("1", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)
    draw.text((0, 15), line1, font=font, fill=255)
    draw.text((0, 35), line2, font=font, fill=255)
    oled.image(image)
    oled.show()

    time.sleep(60)