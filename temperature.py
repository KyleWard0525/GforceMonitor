"""
This file is for reading temperature data
off of the raspberry pi pico's temperature
sensor
"""

import machine
import time
import sys

temp_sensor = machine.ADC(4)     # Port for temp sensor

"""
3.3v/2^(16)-1. Because ADC port has a 12-bit bus but
Pico pads it into a 16-bit bus. ADC requires 3.3v,
it outputs all 1's if powered and all 0's if not powered.
If bus is 16 bits and all bits are set to 1, than max number
is 2^(16)-1 or 65535.
"""
conversion_ratio = 3.3 / 65535

# Probe temperature from sensor
def getTemp(unit):
    global temp_sensor, conversion_ratio
    
    # Get temperature reading from sensor
    sensor_reading = temp_sensor.read_u16() * conversion_ratio
    
    # Convert to celcius
    temp = 27 - (sensor_reading - 0.706)/0.001721
    
    # Check if unit needs to be converted
    if unit == 'f' or unit == "F":
        # Convert to Fahrenheit
        temp = (temp * 1.8) + 32
        
    return temp

def main():
    
    # Get temperature unit from user
    unit = input("Select temp. unit (c=celcius,f=fahrenheit): \t")
    print("\nTemperature unit set!\n")
    time.sleep(1)
    
    
    while True:
        u_input = input("Press enter to get current temperature\n")
        temp = 0
        
        # Pressed enter
        if u_input == "":
            temp = getTemp(unit)
            
            if unit == "f" or unit == "F":
                print("Temperature = %.2f F" % temp)
            else:
                print("Temperature = %.2f C" % temp)
                
        print()
# 
# if __name__ == "__main__":
#     try:
#         main()
#     except KeyboardInterrupt:
#         print("\n\nKeyboardInterruptException\n")
#         sys.exit()
    