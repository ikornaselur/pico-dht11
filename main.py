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

valid_checks = 0
invalid_checks = 0

while True:
    explorer.set_pen(0, 0, 0)
    explorer.clear()
    explorer.set_pen(255, 255, 255)
    try:
        explorer.text("Temperature: {:.01f}C".format(sensor.temperature), 10, 10, 240)
        explorer.text("Humidity: {:.01f}%".format(sensor.humidity), 10, 30, 240)
        valid_checks += 1
    except InvalidChecksum:
        invalid_checks += 1
        explorer.set_pen(255, 0, 0)
        explorer.text("Checksum is invalid", 10, 10, 240)

    explorer.set_pen(255, 255, 255)
    explorer.text("Valid checks: {}".format(valid_checks), 10, 60, 240)
    explorer.text("Invalid checks: {}".format(invalid_checks), 10, 80, 240)
    explorer.text(
        "Ratio: {:.02f}%".format(valid_checks / (valid_checks + invalid_checks) * 100),
        10,
        100,
        240,
    )
    explorer.update()
    utime.sleep(2)
