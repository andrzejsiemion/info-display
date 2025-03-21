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
while True:
    query = f'''
    from(bucket: "{BUCKET}")
      |> range(start: -5m)
      |> filter(fn: (r) => r._measurement == "{MEASUREMENT}")
      |> filter(fn: (r) => r._field == "{FIELD}")
      |> filter(fn: (r) => r.sensor_id == "{SENSOR_ID}")
      |> last()
    '''

    try:
        result = query_api.query(org=ORG, query=query)
        if result and len(result[0].records) > 0:
            value = result[0].records[0].get_value()
            text = f"{FIELD.capitalize()}: {value:.1f}"
        else:
            text = "No data"
    except Exception as e:
        print(f"InfluxDB error: {e}")
        text = "Influx error"

    # Draw and show the text
    image = Image.new("1", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)
    draw.text((10, 25), text, font=font, fill=255)
    oled.image(image)
    oled.show()

    time.sleep(60)