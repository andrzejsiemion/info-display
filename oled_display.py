import os
import time
import signal
import sys
from PIL import Image, ImageDraw, ImageFont
import board
import busio
import adafruit_ssd1306

# Display settings
WIDTH = 128
HEIGHT = 64
UP_FILE = "/app/display/up.txt"
DOWN_FILE = "/app/display/down.txt"

# Init OLED
i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c)
font = ImageFont.load_default()

def clear_display():
    oled.fill(0)
    oled.show()

def signal_handler(sig, frame):
    clear_display()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def read_lines_from_file(path, expected_lines=2):
    try:
        with open(path, "r") as f:
            lines = f.read().splitlines()
            while len(lines) < expected_lines:
                lines.append("")
            return lines[:expected_lines]
    except Exception:
        return [""] * expected_lines

# Main loop
while True:
    up_lines = read_lines_from_file(UP_FILE, 2)
    down_lines = read_lines_from_file(DOWN_FILE, 2)
    all_lines = up_lines + down_lines  # total 4 lines

    # Render to screen
    image = Image.new("1", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)

    for i, line in enumerate(all_lines):
        draw.text((0, i * 15), line, font=font, fill=255)

    oled.image(image)
    oled.show()

    time.sleep(5)