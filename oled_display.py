import time
import board
import busio
import socket
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

# OLED display settings
WIDTH = 128
HEIGHT = 64  # Change to 32 if using a 128x32 display

# Initialize I2C communication
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize OLED display
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c)

def get_ip_address():
    """Returns the IP address of the Raspberry Pi."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Connects to Google DNS to determine network interface
        ip_address = s.getsockname()[0]
        s.close()
    except Exception:
        ip_address = "No IP"
    return ip_address

while True:
    # Get IP address
    ip = get_ip_address()
    
    # Create an image buffer
    image = Image.new("1", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)

    # Load a font
    font = ImageFont.load_default()

    # Display IP address
    draw.text((10, 25), f"IP: {ip}", font=font, fill=255)

    # Show image on the display
    oled.image(image)
    oled.show()

    # Wait for 1 minute before refreshing
    time.sleep(60)