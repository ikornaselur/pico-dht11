import picoexplorer as explorer
import utime
from machine import Pin

from dht import DHT11, InvalidChecksum

width = explorer.get_width()
height = explorer.get_height()
display_buffer = bytearray(width * height * 2)
explorer.init(display_buffer)
explorer.set_backlight(1.0)
explorer.set_pen(0, 0, 0)
explorer.clear()
explorer.update()
explorer.set_pen(255, 255, 255)

pin = Pin(0, Pin.OUT, Pin.PULL_DOWN)
utime.sleep(1)

sensor = DHT11(pin)


while True:
    explorer.set_pen(0, 0, 0)
    explorer.clear()
    explorer.set_pen(255, 255, 255)
    try:
        explorer.text("Temperature: {}C".format(sensor.temperature), 10, 10, 240)
        explorer.text("Humidity: {}%".format(sensor.humidity), 10, 30, 240)
    except InvalidChecksum:
        explorer.set_pen(255, 0, 0)
        explorer.text("Checksum is invalid", 10, 10, 240)
    explorer.update()
    utime.sleep(2)
