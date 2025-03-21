import os
import time
import signal
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import pytz
from loguru import logger

import board
import busio
import adafruit_ssd1306

from influxdb_client import InfluxDBClient

logger.remove() # Remove default Loguru Handler
logger.add(
    sys.stdout, 
    format="[{time:HH:mm:ss}] {level}: {message}", 
    level="INFO"
    )

log_file_path = "/app/logs/logger_screen.log"

logger.add(
    log_file_path, 
    format="[{time:YYYY-MM-DD HH:mm:ss}] {level}: {message}",
    level="INFO", 
    rotation="10MB"
    )

logger.info("Starting info screen logger...")  # Debugging message

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
    logger.info("Stopping. Clearing display.")
    clear_display()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# === Timezone ===
tz_name = os.getenv("TZ", "UTC")
LOCAL_TZ = pytz.timezone(tz_name)

# === InfluxDB Config from Environment ===
INFLUX_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUXDB_TOKEN", "")
ORG = os.getenv("INFLUXDB_ORG", "")
BUCKET = os.getenv("INFLUXDB_BUCKET", "")
MEASUREMENT = os.getenv("INFLUXDB_MEASUREMENT", "")
FIELD_HUMIDITY = os.getenv("INFLUXDB_FIELD_HUMIDITY", "humidity")
FIELD_TEMPERATURE = os.getenv("INFLUXDB_FIELD_TEMPERATURE", "temperature")
SENSOR_IDS = [
    os.getenv("INFLUXDB_SENSOR_ID1", "external_sensor"),
    os.getenv("INFLUXDB_SENSOR_ID2", "internal_sensor")
]

# === InfluxDB Client ===
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
query_api = client.query_api()

# === Build Flux Query ===
def build_query(sensor_id):
    return f'''
    from(bucket: "{BUCKET}")
      |> range(start: -5m)
      |> filter(fn: (r) => r._measurement == "{MEASUREMENT}")
      |> filter(fn: (r) => r.sensor_id == "{sensor_id}")
      |> filter(fn: (r) => r._field == "{FIELD_TEMPERATURE}" or r._field == "{FIELD_HUMIDITY}")
      |> last()
    '''

# === Main Loop ===
while True:
    try:
        lines = []

        for sensor_id in SENSOR_IDS:
            temp_val = hum_val = None
            timestamp = "??"

            result = query_api.query(org=ORG, query=build_query(sensor_id))

            for record in result[0].records if result else []:
                field = record.get_field()
                if field == FIELD_TEMPERATURE:
                    temp_val = record.get_value()
                    timestamp = record.get_time().astimezone(LOCAL_TZ).strftime("%y-%m-%d %H:%M:%S")
                    logger.debug("timestamp: {timestamp}")
                elif field == FIELD_HUMIDITY:
                    hum_val = record.get_value()

            if temp_val is not None and hum_val is not None:
                lines.append(f"{timestamp} {sensor_id}")
                lines.append(f"Temp: {temp_val:.1f}°C  Hum: {hum_val:.1f}%")
            else:
                lines.append(f"{sensor_id} - No data")
                lines.append("")

    except Exception as e:
        logger.info(f"InfluxDB error: {e}")
        lines = ["Influx error", ""]

    # Draw to OLED
    image = Image.new("1", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)

    for i, line in enumerate(lines[:4]):
        draw.text((0, i * 15), line, font=font, fill=255)

    oled.image(image)
    oled.show()

    time.sleep(10)