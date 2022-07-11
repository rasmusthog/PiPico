import machine
import time


LM35 = machine.ADC(28)
RP2040 = machine.ADC(4)

conversion_factor = 3.3 / 65535

while True:
    tempLM35 = 0
    tempRP2040 = 0
    for i in range(100):
        tempLM35_raw = LM35.read_u16()

        convert_voltage_LM35 = tempLM35_raw * conversion_factor
        tempLM35 += convert_voltage_LM35 / (10.0 / 1000)

        tempRP2040_raw = RP2040.read_u16()

        convert_voltage_RP2040 = tempRP2040_raw * conversion_factor
        tempRP2040 += 27 - (convert_voltage_RP2040 - 0.706)/0.001721 
    
    print("LM35: ",round(tempLM35/100, 1), "C", "RP2040: ", round(tempRP2040/100, 1), "C", sep=" ")
    
    time.sleep(2)