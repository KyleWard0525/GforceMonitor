"""
This file is a controller script for an anode RGB
LED. It is being developed specifically to support GMonitor but
can be used for any project

kward
"""
from machine import Pin
import time

# Main class
class LedController:

    """
    Initialize controller
    
    rPin: red gpio pin
    gPin: green gpio pin
    bPin: blue gpio pin
    """
    def __init__(self, rPin, gPin, bPin):
        
        # Check pins
        if not type(rPin) == int:
            # Print error message and fail instance creation
            print("Error in rgbLed.__init__(): rPin must be an integer")
            return None
        elif not type(gPin) == int:
            # Print error message and fail instance creation
            print("Error in rgbLed.__init__(): gPin must be an integer")
            return None
        elif not type(bPin) == int:
            # Print error message and fail instance creation
            print("Error in rgbLed.__init__(): bPin must be an integer")
            return None
        
        self.red = Pin(rPin, Pin.OUT)
        self.green = Pin(gPin, Pin.OUT)
        self.blue = Pin(bPin, Pin.OUT)
            
    """
    Display colors indefinetly
    """
    def solidRed(self):
        self.red.high()
        self.green.low()
        self.blue.low()
        
    def solidGreen(self):
        self.red.low()
        self.green.high()
        self.blue.low()
        
    def solidBlue(self):
        self.red.low()
        self.green.low()
        self.blue.high()
        
    def solidPurple(self):
        self.red.high()
        self.green.low()
        self.blue.high()
        
    def solidYellow(self):
        self.red.high()
        self.green.high()
        self.blue.low()
        
    def solidCyan(self):
        self.red.low()
        self.green.high()
        self.blue.high()
    
    
    # Run set of tests
    def test(self):
        tests = {
            'red': self.solidRed,
            'green': self.solidGreen,
            'blue': self.solidBlue,
            'purple': self.solidPurple,
            'yellow': self.solidYellow,
            'cyan': self.solidCyan
            }
        
        print("\n\nStarting RGB LED TESTS..\n\n")
        time.sleep(1)
        
        for test in tests:
            print("Test: " + test + "..")
            tests[test]()
            time.sleep(1)
            
        self.clear()
    
    # Turn off led
    def clear(self):
        self.red.low()
        self.green.low()
        self.blue.low()