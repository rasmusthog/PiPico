# Class to read temperature from the TMP117 I2C temperature sensor

# Based on:
# https://github.com/CoreElectronics/CE-PiicoDev-TMP117-MicroPython-Module
#  by Michael Ruppe at Core Electronics MAR 2021

# Register definitions
REG_TEMPC = 0x00

class TMP117(object):    

    _baseAddr = 0x48

    def __init__(self, i2c_bus):
        
        self._tmp_addr = self._baseAddr
        self._tmp_i2c = i2c_bus
        self._chip_id = self._tmp_i2c.readfrom_mem(self._tmp_addr, 0xD0, 2)


    def readT(self):
        data = self._tmp_i2c.readfrom_mem(self._tmp_addr, REG_TEMPC, 2)
        data = int.from_bytes(data, 'big')
        
        # Handles negatives (how?)
        if data >= 0x8000:
            data = -256.0 + (data - 0x8000) * 7.8125e-3
        
        else:
            data = data * 7.8125e-3

        return data
