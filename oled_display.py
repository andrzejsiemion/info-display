import time
import board
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

# OLED display settings
WIDTH = 128
HEIGHT = 64  # Change to 32 if using a 128x32 display

# Initialize I2C communication (for Raspberry Pi, use bus 1)
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize OLED display
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Clear the display
oled.fill(0)
oled.show()

# Create an image buffer
image = Image.new("1", (WIDTH, HEIGHT))
draw = ImageDraw.Draw(image)

# Load a font
font = ImageFont.load_default()

# Display text
text = "Hello, World!"
draw.text((10, 25), text, font=font, fill=255)

# Show image on the display
oled.image(image)
oled.show()

# Keep the text visible for 10 seconds
time.sleep(10)

# Clear the display before exit
oled.fill(0)
oled.show()
