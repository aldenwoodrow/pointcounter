{\rtf1\ansi\ansicpg1252\cocoartf2758
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 from machine import Pin, SPI\
import sh1107\
import utime\
import math\
import framebuf\
import freesans20\
import writer\
from time import sleep\
\
import lowpower\
\
# Initialize SPI and OLED as previously done\
spi = SPI(1, baudrate=2000000, sck=Pin(10), mosi=Pin(11))\
cs = Pin(9, Pin.OUT)\
dc = Pin(8, Pin.OUT)\
rst = Pin(12, Pin.OUT)\
oled = sh1107.SH1107_SPI(128, 64, spi, dc, rst, cs)\
\
# Button setup\
button1 = Pin(17, Pin.IN, Pin.PULL_UP) \
button2 = Pin(15, Pin.IN, Pin.PULL_UP)\
\
DORMANT_PIN1 = 17\
DORMANT_PIN2 = 15\
\
try:\
    with open('pcount.txt', 'r') as f:\
        pCount = int(f.read())\
except OSError:\
    pCount = 0\
\
def save_pcount():\
    with open('pcount.txt', 'w') as f:\
        f.write(str(pCount))\
\
# Timer variable\
timer = 0\
display_on = False\
print("running")\
\
# Initialize last_button_check\
last_button_check = utime.ticks_ms()\
\
#from https://javl.github.io/image2cpp/\
\
byte_array = bytearray([\
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x01, 0x00, 0x00, 0x00, \
	0x00, 0x00, 0x00, 0xc0, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x60, 0x06, 0x00, 0x00, 0x00, \
	0x00, 0x00, 0x00, 0x30, 0x0c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x18, 0x18, 0x00, 0x00, 0x00, \
	0x00, 0x00, 0x00, 0x0c, 0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x06, 0x60, 0x00, 0x00, 0x00, \
	0x00, 0x00, 0x00, 0x03, 0xc0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x81, 0x80, 0x01, 0x00, 0x00, \
	0x00, 0x00, 0xc0, 0xc0, 0x01, 0x03, 0x00, 0x00, 0x00, 0x00, 0x60, 0x80, 0x00, 0x06, 0x00, 0x00, \
	0x00, 0x00, 0x30, 0x00, 0x00, 0x0c, 0x00, 0x00, 0x00, 0x00, 0x18, 0x00, 0x00, 0x18, 0x00, 0x00, \
	0x00, 0x00, 0x0c, 0x20, 0x00, 0x30, 0x00, 0x00, 0x00, 0x00, 0x06, 0x71, 0x60, 0x60, 0x00, 0x00, \
	0x00, 0x00, 0x83, 0x23, 0x90, 0xc0, 0x00, 0x00, 0x00, 0x80, 0x01, 0x01, 0x08, 0x81, 0x01, 0x00, \
	0x00, 0xc0, 0x00, 0x00, 0xfc, 0x03, 0x03, 0x00, 0x00, 0x60, 0x20, 0x00, 0xff, 0x07, 0x06, 0x00, \
	0x00, 0x30, 0x70, 0xc0, 0xff, 0x0f, 0x0c, 0x00, 0x00, 0x18, 0x20, 0xe0, 0xff, 0x1f, 0x18, 0x00, \
	0x00, 0x0c, 0x06, 0xf0, 0xff, 0xff, 0x30, 0x00, 0x00, 0x86, 0x1f, 0xf8, 0xff, 0xff, 0x61, 0x00, \
	0x00, 0xe3, 0x7f, 0xfc, 0xff, 0xff, 0xc3, 0x00, 0x80, 0xf1, 0xff, 0xfe, 0xff, 0xff, 0x87, 0x01, \
	0xc0, 0xf8, 0xff, 0xff, 0xff, 0xff, 0x0f, 0x03, 0x60, 0xfc, 0xff, 0xff, 0xff, 0xff, 0x1f, 0x06, \
	0x30, 0xfe, 0xff, 0xff, 0xff, 0xff, 0x3f, 0x0c, 0x18, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x18, \
	0x0c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x30, 0x06, 0x6f, 0xfc, 0x4d, 0xb7, 0x73, 0x7b, 0x60, \
	0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x60, 0x0c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x30, \
	0x18, 0x0c, 0x00, 0x00, 0x01, 0x00, 0x60, 0x18, 0x30, 0x18, 0x00, 0x80, 0x03, 0x00, 0x30, 0x0c, \
	0x60, 0x30, 0x00, 0xc0, 0x06, 0x00, 0x18, 0x06, 0xc0, 0x60, 0x00, 0x60, 0x0c, 0x00, 0x0c, 0x03, \
	0x80, 0xc1, 0x00, 0x30, 0x18, 0x00, 0x86, 0x01, 0x00, 0x83, 0x01, 0x18, 0x30, 0x00, 0xc3, 0x00, \
	0x00, 0x06, 0x03, 0x0c, 0x60, 0x80, 0x61, 0x00, 0x00, 0x0c, 0x06, 0x06, 0xc0, 0xc0, 0x30, 0x00, \
	0x00, 0x18, 0x0c, 0x03, 0x80, 0x61, 0x18, 0x00, 0x00, 0x30, 0x98, 0x01, 0x00, 0x33, 0x0c, 0x00, \
	0x00, 0x60, 0xf0, 0x00, 0x00, 0x1e, 0x06, 0x00, 0x00, 0xc0, 0x60, 0x38, 0x1c, 0x0c, 0x03, 0x00, \
	0x00, 0x80, 0x01, 0x78, 0x1e, 0x80, 0x01, 0x00, 0x00, 0x00, 0x03, 0xf8, 0x1f, 0xc0, 0x00, 0x00, \
	0x00, 0x00, 0x06, 0xf8, 0x1f, 0x60, 0x00, 0x00, 0x00, 0x00, 0x0c, 0x38, 0x1c, 0x30, 0x00, 0x00, \
	0x00, 0x00, 0x18, 0xf8, 0x1f, 0x18, 0x00, 0x00, 0x00, 0x00, 0x30, 0xe0, 0x07, 0x0c, 0x00, 0x00, \
	0x00, 0x00, 0x60, 0x80, 0x01, 0x06, 0x00, 0x00, 0x00, 0x00, 0xc0, 0x00, 0x00, 0x03, 0x00, 0x00, \
	0x00, 0x00, 0x80, 0x01, 0x80, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0xc0, 0x00, 0x00, 0x00, \
	0x00, 0x00, 0x00, 0x06, 0x60, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0c, 0x30, 0x00, 0x00, 0x00, \
	0x00, 0x00, 0x00, 0x18, 0x18, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x30, 0x0c, 0x00, 0x00, 0x00, \
	0x00, 0x00, 0x00, 0x60, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xc0, 0x03, 0x00, 0x00, 0x00, \
	0x00, 0x00, 0x00, 0x80, 0x01, 0x00, 0x00, 0x00\
])\
\
def display_image(byte_array):\
    img_width = 62  # width of the image in pixels\
    img_height = 62  # height of the image in pixels\
    bytes_per_row = math.ceil(img_width / 8)\
\
    oled.fill(0)  # Clear the display\
\
    for y in range(img_height):\
        for x in range(img_width):\
            # Calculate which byte and which bit represents this pixel\
            byte_index = x // 8 + y * bytes_per_row\
            bit_index = x % 8\
\
            # Set the pixel if the corresponding bit is 1\
            if byte_array[byte_index] & (1 << bit_index):\
                oled.pixel(x, y, 1)\
\
    # Update the display to show the image\
    oled.show()\
\
def display_text():\
\
    # Display text to the right of the image\
    title = "Points"\
    char_width = 8  # Width of each character in pixels\
    display_width = 128 - 64  # Adjust width for the text area\
    title_width = len(title) * char_width\
    x_start_title = 64 + ((display_width - title_width) // 2)  # Calculate starting x position\
\
    oled.text(title, x_start_title, 15, 1)  # Display title\
\
    # Display text to the right of the image\
    char_width = 8  # Width of each character in pixels\
    display_width = 128 - 64  # Adjust width for the text area\
\
    # Center-align pCount\
    pCount_str = str(pCount)\
    pCount_width = len(pCount_str) * char_width\
    x_start_pCount = 64 + ((display_width - pCount_width) // 2)  # Calculate starting x position\
    \
    font_writer = writer.Writer(oled, freesans20)\
    font_writer.set_textpos(85, 25)\
    font_writer.printstring(pCount_str)\
\
    #oled.text(pCount_str, x_start_pCount, 30, 1)  # Display pCount\
\
oled.poweron()\
\
while True:\
    # Check if button 1 is pressed\
    if not button1.value():\
        if display_on:\
            pCount += 1  # Increment pCount when display is turned on\
            save_pcount()\
            display_image(byte_array)\
            display_text()\
            oled.show()\
            timer = 0\
\
        else:\
            # If the display is off, toggle it on and increment pCount\
            oled.poweron()\
            display_image(byte_array)\
            display_text()\
            oled.show()\
            display_on = True\
            timer = 0\
            \
        utime.sleep(0.2)  # Debounce delay\
    \
\
    # Check if button 2 is pressed\
    if not button2.value():\
        if display_on:\
            pCount -= 1  # Increment pCount when display is turned on\
            save_pcount()\
            display_image(byte_array)\
            display_text()\
            oled.show()\
            timer = 0\
 \
        else:\
            # If the display is off, toggle it on and increment pCount\
            oled.poweron()\
            display_on = True\
            display_image(byte_array)\
            display_text()\
            oled.show()\
            timer = 0\
        \
        utime.sleep(0.2)  # Debounce delay        \
        \
    # Increment the timer\
    timer += utime.ticks_diff(utime.ticks_ms(), last_button_check)\
\
    # Check if the timer exceeds 20 seconds\
    if timer >= 10000:\
        # Put the Pico into deep sleep\
        display_on = False\
        oled.poweroff()\
        print("sleeping") \
        lowpower.dormant_until_pins([DORMANT_PIN1, DORMANT_PIN2])\
        print("awake")\
        oled.poweron()\
        display_on = True\
        timer = 0\
\
    \
    # Store the timestamp of the last button check\
    last_button_check = utime.ticks_ms()\
}