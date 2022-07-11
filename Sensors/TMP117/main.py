from machine import Pin, I2C
from tmp117 import TMP117
import utime

sdaPIN = Pin(14)
sclPIN = Pin(15)

i2c = I2C(1, sda=sdaPIN, scl=sclPIN, freq=400000)

devices = i2c.scan()

if len(devices) == 0:
    print("No I2C device found...")
else:
    print(f'{len(devices)} I2C devices found:')

for i, device in enumerate(devices):
    print(f'#{i+1}: {hex(device)}')

tmp117 = TMP117(i2c_bus=i2c)

while True:

    tempC = 0
    for i in range(100):
        tempC += tmp117.readT()

    
    print('Temperature: ', round(tempC/100, 1), 'C')
    utime.sleep(1)