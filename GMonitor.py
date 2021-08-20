"""
This file contains the code for the G-force monitor
class

Author: Kyle Ward (kward)
"""
from machine import Pin
from temperature import getTemp
import icm20948
import time
import sys
from LedController import LedController

# Main G-force Monitor Class
class GMonitor:
    
    # Initialize class
    def __init__(self):
        # 2013 V6 Mustang maximum lateral force tolerance
        self.maxLatForce = 0.95
        
        self.lights = {
    
        # Vertical leds ('M' = middle led)
        "2U": Pin(16, Pin.OUT),
        "1U": Pin(17, Pin.OUT),
        "M": {
            'R': Pin(9,Pin.OUT),
            'G': Pin(8,Pin.OUT),
            'B': Pin(0,Pin.OUT)
        },
        "1D": Pin(19, Pin.OUT),
        "2D": Pin(20, Pin.OUT),
    
        # Horizontal leds
        "2L": Pin(13, Pin.OUT),
        "1L": Pin(12, Pin.OUT),
        "1R": Pin(11, Pin.OUT),
        "2R": Pin(10, Pin.OUT)
    }
        self.imu = icm20948.ICM20948()
        self.rgb = LedController(9,8,0)
        
        print("GMonitor initialized")
        
    # Test LED functionality and Pin correctness
    def lightTest(self):
        # Blink each light
        for pin in self.lights:
            print("Blinking light: " + str(pin))
            self.lights[pin].toggle()
            time.sleep(1)
            self.lights[pin].toggle()
            
    # Test RGB LED
    def rgbTest(self):
        
        self.rgb.test()
        
        self.cleanup()
        
            
    # Compute acceleration values
    def pollAcceleration(self):
        accelOffset = 16384 # From LSB to g
        
        self.imu.GyroAccelRead()
    
        self.ax = icm20948.Accel[0] / accelOffset # Longitudinal Acceleration
        self.ay = icm20948.Accel[1] / accelOffset # Lateral Acceleration 
        self.az = icm20948.Accel[2] / accelOffset # Vertical acceleration
        
    # Flash all LEDs in the direction in which it is exceeding
    # 1.25x the tolerance
    def flashWarning(self, side, delay):
        numBlinks = 2
        
        # REMOVE AFTER DEBUGGING
        print("Flashing warning...\nDelay = " + str((delay*1000)) + " ms\n")
        
        if delay < 0.05:
            delay = 0.050
        elif delay > 0.2:
            delay = 0.200
        
        # Upward LEDs
        if side == "up":
            # Flash warning to user
            for i in range(numBlinks):
                self.lights["M"].toggle()
                self.lights["1U"].toggle()
                self.lights["2U"].toggle()
                
                time.sleep(delay)
        # Left LEDs
        if side == "left":
            # Flash warning to user
            for i in range(numBlinks):
                self.lights["1L"].toggle()
                self.lights["2L"].toggle()
                time.sleep(delay)
                
        # Right LEDs
        if side == "right":
            # Flash warning to user
            for i in range(numBlinks):
                self.lights["1R"].toggle()
                self.lights["2R"].toggle()
                time.sleep(delay)
                
        # Down (Rearward) LEDs
        if side == "down":
            # Flash warning to user
            for i in range(numBlinks):
                self.lights["M"].toggle()
                self.lights["1D"].toggle()
                self.lights["2D"].toggle()
                
                time.sleep(delay)  
        
        self.cleanup()
                
        
    # Light up leds relative to acceleration
    # latTolerance = lateral g's per led
    # longTolF = longitudinal g's per front led
    # longTolR = longitudinal g's per rear led
    # pollRate in hz
    def monitor(self, latTolerance, longTolF, longTolR, pollRateHz):
        print("\nMonitoring...")
        
        print("\nLateral tolerance: " + str(latTolerance) + " g")
        print("Longitudinal acceleration tolerance: " + str(longTolR) + " g")
        print("Logitudinal braking tolerance: " + str(longTolF) + " g")
        
        while True:
            self.pollAcceleration()
            
            # Compute time delay
            delay = 1 / pollRateHz
            
            # Check vertical acceleration
            if self.az > 0.5:
                self.lights["M"].value(1)
            else:
                self.lights["M"].value(0)
            
            # Check lateral acceleration
            if self.ax > latTolerance or self.ax < -latTolerance:
                # Check direction
                if self.ax < 0:
                    # Right
                    numLeds = round(abs(self.ax / latTolerance))
                    
                    # Approaching slip angle
                    if self.ax < -(self.maxLatForce - 0.1):
                        warningDelay = 0.1 / abs(self.ax/latTolerance)
                        
                        # Flash warning
                        self.flashWarning("right", warningDelay)
                        
                    else:
                        if numLeds == 1:
                            self.lights["1R"].toggle()
                            time.sleep(delay)
                            self.lights["1R"].toggle()
                        elif numLeds == 2:
                            self.lights["1R"].toggle()
                            self.lights['2R'].toggle()
                            time.sleep(delay)
                            self.lights['1R'].toggle()
                            self.lights['2R'].toggle()
                        
                    
                    
                # Left
                else: 
                    numLeds = round(abs(self.ax / latTolerance))
                    
                    # Approaching slip angle
                    if self.ax > self.maxLatForce - 0.1:
                        warningDelay = 0.1 / abs(self.ax/latTolerance)
                        
                        # Flash warning
                        self.flashWarning("left", warningDelay)
                    else:
                        if numLeds == 1:
                            self.lights["1L"].toggle()
                            time.sleep(delay)
                            self.lights["1L"].toggle()
                        elif numLeds == 2:
                            self.lights["1L"].toggle()
                            self.lights['2L'].toggle()
                            time.sleep(delay)
                            self.lights['1L'].toggle()
                            self.lights['2L'].toggle()
                            
            # Check direction of acceleration
            if self.ay > 0:
                # Forward
                numLeds = round(abs(self.ay/longTolR))
                
                if numLeds == 1:
                    self.lights["1D"].toggle()
                    time.sleep(delay)
                    self.lights["1D"].toggle()
                elif numLeds == 2:
                    self.lights["1D"].toggle()
                    self.lights['2D'].toggle()
                    time.sleep(delay)
                    self.lights['1D'].toggle()
                    self.lights['2D'].toggle()
                    
            # Braking
            elif self.ay < 0:
                numLeds = round(abs(self.ay/longTolF))
                
                if numLeds == 1:
                    self.lights["1U"].toggle()
                    time.sleep(delay)
                    self.lights["1U"].toggle()
                elif numLeds == 2:
                    self.lights["1U"].toggle()
                    self.lights['2U'].toggle()
                    time.sleep(delay)
                    self.lights['1U'].toggle()
                    self.lights['2U'].toggle()
                    
                    
                        
            # Reset middle LED
            self.lights["M"].value(0)
        
    
            
    # Free system resources and disable all GPIO
    def cleanup(self):
        # Disable all GPIO
        for pin in self.lights:
            # Check if pin is rgb led
            if pin == "M":
                self.lights[pin]['R'].low()
                self.lights[pin]['G'].low()
                self.lights[pin]['B'].low()
                continue
            
            self.lights[pin].value(0)
                
                
def main():
    
    # Initialize gforce monitor
    gfm = GMonitor()
    
    print("Current temperature: " + str(getTemp('f')) + " F")
    
    
    #gfm.monitor(0.4,1.0,0.3,100)
    gfm.rgbTest()
    
    # Cleanup
    gfm.cleanup()
    
    
    
    
if __name__ == "__main__":
    main()