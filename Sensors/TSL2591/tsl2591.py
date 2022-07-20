'''Based on https://github.com/jfischer/micropython-tsl2591/blob/master/tsl2591.py
And: https://docs.circuitpython.org/projects/tsl2591/en/latest/_modules/adafruit_tsl2591.html

More documents here: https://ams.com/tsl25911#tab/documents'''

# Class to read temperature from the TSL2591 I2C light sensor

# Register definitions
ADDRESS                 = 0x29
COMMAND                 = 0xA0

# REGISTER DEFINITONS
REG_ENABLE              = 0x00 # Enables states and interrupts (R/W)
REG_CONFIG              = 0x01 # ALS gain and integration time configuration (R/W)
REG_AILTL               = 0x04 # ALS interrupt low threshold low byte (R/W)
REG_AILTH               = 0x05 # ALS interrupt low threshold high byte (R/W)
REG_AIHTL               = 0x06 # ALS interrupt high threshold low byte (R/W)
REG_AIHTH               = 0x07 # ALS interrupt high threshold high byte (R/W)
REG_NPAILTL             = 0x08 # No Persist ALS interrupt low threshold low byte (R/W)
REG_NPAILTH             = 0x09 # No Persist ALS interrupt low threshold high byte (R/W)
REG_NPAIHTL             = 0x0A # No Persist ALS interrupt high threshold low byte (R/W)
REG_NPAIHTH             = 0x0B # No Persist ALS interrupt high threshold high byte (R/W)
REG_PERSIST             = 0x0C # Interrupt persistence filter (R/W)
REG_PID                 = 0x11 # Package ID (R)
REG_ID                  = 0x12 # Device ID (R)
REG_STATUS              = 0x13 # Device status (R)
REG_C0DATAL             = 0x14 # CH0 ADC low data byte (R)
REG_C0DATAH             = 0x15 # CH0 ADC high data byte (R)
REG_C1DATAL             = 0x16 # CH1 ADC low data byte (R)
REG_C1DATAH             = 0x17 # CH1 ADC high data byte (R)


ENABLE_POWEROFF         = 0x00
ENABLE_POWERON          = 0x01 # Power ON. This field activates the internal oscillator to permit the timers and ADC channels to operate. Writing a one activates the oscillator. Writing a zero disables the oscillator
ENABLE_AEN              = 0x02 # ALS Enable. This field activates ALS function. Writing a one activates the ALS. Writing a zero disables the ALS.
ENABLE_AIEN             = 0x10 # ALS Interrupt Enable. When asserted permits ALS interrupts to be generated, subject to the persist filter.

# Integration times
INTEGRATION_TIME_100MS  = 0x00
INTEGRATION_TIME_200MS  = 0x10
INTEGRATION_TIME_300MS  = 0x20
INTEGRATION_TIME_400MS  = 0x30
INTEGRATION_TIME_500MS  = 0x40
INTEGRATION_TIME_600MS  = 0x50

MAX_COUNT_100MS         = 37888
MAX_COUNT               = 65535

# Gain
GAIN_LOW                = 0x00
GAIN_MED                = 0x10
GAIN_HIGH               = 0x20
GAIN_MAX                = 0x30

# Device specific factors
DEVICE_FACTOR           = 408
LUX_COEFFICIENT_B       = 1.64
LUX_COEFFICIENT_C       = 0.59
LUX_COEFFICIENT_D       = 0.86


def _bytes_to_int(data):
    return data[0] + (data[1]<<8)


from machine import I2C, Pin
import utime

class I2CBus:
    def __init__(self, scl=15, sda=14):
        self.i2c = I2C(1, scl=Pin(scl), sda=Pin(sda))

    def write_byte_data(self, addr, cmd, val):
        buf = bytes([cmd, val])
        self.i2c.writeto(addr, buf)

    def read_word_data(self, addr, cmd):
        assert cmd < 256
        buf = bytes([cmd])
        self.i2c.writeto(addr, buf)
        data = self.i2c.readfrom(addr, 4)
        return _bytes_to_int(data)


class TSL2591(object):

    def __init__(self, scl=15, sda=14, integration_time=INTEGRATION_TIME_100MS, gain=GAIN_LOW):

        self.addr = ADDRESS
        self.i2c = I2CBus(scl=scl, sda=sda)
        self.integration_time = integration_time 
        self.gain = gain 
        self.maxcount = MAX_COUNT_100MS if self.integration_time == INTEGRATION_TIME_100MS else MAX_COUNT
        self.set_integration_time(self.integration_time)
        self.set_gain(self.gain)
        self.disable()

    def set_integration_time(self, integration_time):
        self.enable()
        self.integration_time = integration_time
        self.i2c.write_byte_data(
                                ADDRESS, 
                                COMMAND | REG_CONFIG, 
                                self.integration_time | self.gain
                                )

        self.maxcount = MAX_COUNT_100MS if self.integration_time == INTEGRATION_TIME_100MS else MAX_COUNT
        self.disable()


    def set_gain(self, gain):
        self.enable()
        self.gain = gain
        self.i2c.write_byte_data(
                                ADDRESS,
                                COMMAND | REG_CONFIG,
                                self.integration_time | self.gain
                                )
        self.disable()

    def get_luminosity(self):
        self.enable()
        utime.sleep(0.120*self.integration_time+1)

        full_spectrum   = self.i2c.read_word_data(
                                ADDRESS,
                                COMMAND | REG_C0DATAL
                                )
        
        ir_spectrum     = self.i2c.read_word_data(
                                ADDRESS,
                                COMMAND | REG_C1DATAL
                                )

        self.disable()

        print(full_spectrum, ir_spectrum)

        return full_spectrum, ir_spectrum


    def get_visible_visible(self):
        full_spectrum, ir_spectrum = self.get_luminosity()

        return full_spectrum - ir_spectrum


    def calculate_lux(self, full_spectrum, ir_spectrum):

        integration_times = {
            INTEGRATION_TIME_100MS: 100,
            INTEGRATION_TIME_200MS: 200,
            INTEGRATION_TIME_300MS: 300,
            INTEGRATION_TIME_400MS: 400,
            INTEGRATION_TIME_500MS: 500,
            INTEGRATION_TIME_600MS: 600
        }

        gains = {
            GAIN_LOW: 1,
            GAIN_MED: 25,
            GAIN_HIGH: 428,
            GAIN_MAX: 9876
        }

        atime = integration_times[self.integration_time]
        again = gains[self.gain]

        
        if full_spectrum >= self.maxcount or ir_spectrum >= self.maxcount:
            raise RuntimeError('Sensor saturated. Adjust gain and/or integration time.')

        counts_per_lux = (atime * again) / DEVICE_FACTOR

        lux1 = (full_spectrum - (LUX_COEFFICIENT_B * ir_spectrum)) / counts_per_lux
        lux2 = ((LUX_COEFFICIENT_C*full_spectrum) - (LUX_COEFFICIENT_D*ir_spectrum)) / counts_per_lux


        return max(lux1, lux2)

    def sample(self):
        full_spectrum, ir_spectrum = self.get_luminosity()

        return self.calculate_lux(full_spectrum, ir_spectrum)

    def enable(self):
        self.i2c.write_byte_data(
                                ADDRESS, 
                                COMMAND | REG_ENABLE,
                                ENABLE_POWERON | ENABLE_AEN |  ENABLE_AIEN
                                )


    def disable(self):
        self.i2c.write_byte_data(
                                ADDRESS,
                                COMMAND | REG_ENABLE,
                                ENABLE_POWEROFF
                                )
