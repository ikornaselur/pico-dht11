import array

import utime
from machine import Pin


class InvalidChecksum(Exception):
    pass


class DHT11:
    high_level: int = 50
    max_unchanged: int = 100
    min_interval_us: int = 200000

    _temperature: int
    _humidity: int

    def __init__(self, pin):
        self._pin = pin
        self._last_measure = utime.ticks_us()
        self._temperature = -1
        self._humidity = -1

    def measure(self):
        current_ticks = utime.ticks_us()
        if utime.ticks_diff(
            current_ticks, self._last_measure
        ) < self.min_interval_us and (self._temperature > -1 or self._humidity > -1):
            # Less than a second since last read, which is too soon according
            # to the datasheet
            return

        self._send_init_signal()
        pulses = self._capture_pulses()
        buffer = self._convert_pulses_to_buffer(pulses)
        self._verify_checksum(buffer)

        self._humidity = buffer[0]
        self._temperature = buffer[2]
        self._last_measure = utime.ticks_us()

    @property
    def humidity(self):
        self.measure()
        return self._humidity

    @property
    def temperature(self):
        self.measure()
        return self._temperature

    def _send_init_signal(self):
        self._pin.init(Pin.OUT, Pin.PULL_DOWN)
        self._pin.value(1)
        utime.sleep_ms(50)
        self._pin.value(0)
        utime.sleep_ms(18)

    def _capture_pulses(self):
        self._pin.init(Pin.IN, Pin.PULL_UP)
        val = 1
        transitions = []
        unchanged = 0
        while unchanged < self.max_unchanged:
            if val != self._pin.value():
                transitions.append(utime.ticks_us())
                val = 1 - val
                unchanged = 0
            else:
                unchanged += 1
        self._pin.init(Pin.OUT, Pin.PULL_DOWN)

        # We only want the last 81 transitions to calculate 80 bits
        transitions = transitions[-81:]

        # Return the pulse times
        return [
            utime.ticks_diff(transitions[i + 1], transitions[i])
            for i in range(len(transitions) - 1)
        ]

    def _convert_pulses_to_buffer(self, pulses):
        """Convert a list of 80 pulses into a 5 byte buffer

        The resulting 5 bytes in the buffer will be:
            0: Integral relative humidity data
            1: Decimal relative humidity data
            2: Integral temperature data
            3: Decimal temperature data
            4: Checksum
        """
        # Convert the pulses to 40 bits
        binary = 0
        for idx in range(0, len(pulses), 2):
            binary = binary << 1 | int(pulses[idx] > self.high_level)

        # Split into 5 bytes
        buffer = array.array("B")
        for shift in range(4, -1, -1):
            buffer.append(binary >> shift * 8 & 0xFF)

        return buffer

    def _verify_checksum(self, buffer):
        # Calculate checksum
        checksum = 0
        for buf in buffer[0:4]:
            checksum += buf
        if checksum & 0xFF != buffer[4]:
            raise InvalidChecksum()
