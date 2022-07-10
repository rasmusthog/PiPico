from machine import Pin, I2C
from bmp180 import BMP180
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



bmp = BMP180(i2c_bus=i2c)

while True:
    tempC = 0
    p = 0
    alt = 0

    for i in range(100):
        tempC += bmp.temperature
        p += bmp.pressure
        alt += bmp.altitude

    print(f'Temperature: {round(tempC/100,1)} C \t Pressure: {round((p / 101325)/100,1)} atm \t Altitude: {round(alt/100, 1)} m')

    utime.sleep(1)


