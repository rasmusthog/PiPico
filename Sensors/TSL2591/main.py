from machine import Pin
from tsl2591 import TSL2591
#from tsl_org import Tsl2591
import utime

sdaPIN = 14
sclPIN = 15

tsl = TSL2591(scl=15, sda=14)


while True:
    utime.sleep(1)
    print('Lux:', tsl.sample())