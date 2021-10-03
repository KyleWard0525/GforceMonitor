"""
This file contains the code for the G-force monitor
class

MicroPython runs two scripts at power on: boot.py and main.py
in that order.

Author: Kyle Ward (kward)
"""

from LEDController import LedController # RGB LED Controller
from machine import Pin # RPi Pico Hardware Interface
from temperature import getTemp # Get current temperature
from DataLogger import Logger # For computing and storing performance metrics
import icm20948 # IMU API
import time # sleep and timing operations
import sys # python system operations
import gc # Garbage collection

# Main G-force Monitor Class
class GMonitor:
    
    # Initialize class
    def __init__(self):
        # 2013 V6 Mustang maximum lateral force tolerance
        self.maxLatForce = 0.95
        
        # Set ride mode button Pin
        self.btnModeSel = Pin(1, Pin.IN, Pin.PULL_UP)
        
        # Set button pin to signal data logger to start
        self.btnStartLogger = Pin(18, Pin.IN, Pin.PULL_UP)
        self.enableLogger = False
        
        # Create map of LEDs
        self.lights = {
    
        # Vertical leds ('M' = middle led)
        "2U": Pin(16, Pin.OUT),
        "1U": Pin(17, Pin.OUT),
        "M": LedController(9,8,0),
        "1D": Pin(19, Pin.OUT),
        "2D": Pin(20, Pin.OUT),
    
        # Horizontal leds
        "2L": Pin(13, Pin.OUT),
        "1L": Pin(12, Pin.OUT),
        "1R": Pin(11, Pin.OUT),
        "2R": Pin(10, Pin.OUT),
        
        # Other various signal lights
        "logger": Pin(14, Pin.OUT) 
    }
        # Define ride modes
        self.modes = {
            
            # For showing off the device in a low-acceleration environment
            "tech-demo": {
                "latTolerance": 0.25, # Lateral acceleration tolerance
                "longTolF": 0.4, # Braking tolerance
                "longTolR": 0.2, # Forward acceleration tolerance
                "color": "purple", # Display color for RGB led
                "name": "tech-demo" # Name of the mode
            },
            
            # For normal usage
            "normal": {
                "latTolerance": 0.3,    
                "longTolF": 0.6,
                "longTolR": 0.25,
                "color": "yellow",
                "name": "normal"
            },
            
            # For usage when the vehicle will be driven hard on normal roads
            "sport": {
                "latTolerance": 0.35,
                "longTolF": 1.0,
                "longTolR": 0.27,
                "color": "cyan",
                "name": "sport"
            },
            
            # For usage on a track or closed course
            "race": {
                "latTolerance": 0.4,
                "longTolF": 1.2,
                "longTolR": 0.3,
                "color": "red",
                "name": "race"
            }
            
        }
        
        # Define default ride mode
        self.rideMode = self.modes["normal"]
        
        # Set center LED to indicate ride mode
        self.lights["M"].colors[self.rideMode["color"]]()
        
        # Create IMU
        self.imu = icm20948.ICM20948()
        
        # Set system poll rate (Hz) of IMU
        self.pollRateHz = 1000 # 1kHz (1ms)
        
        # Set initial time point
        self.start_time = time.time()

        # Create data logger object
        self.logger = Logger(self) # Default poll rate 100hz (10ms)
        self.logger.computeMetrics()
        
        print("GMonitor initialized")
        
    # Handle button press and switch ride mode
    def nextRideMode(self):
        # Set ride mode to the next in the dict
        tempList = list(self.modes)

        # Set new ride mode
        nextIdx = tempList.index(self.rideMode['name'])+1
        
        # Check if next mode is out of bounds
        if nextIdx > len(self.modes)-1:
            nextIdx = 0
        
        self.rideMode = self.modes[tempList[nextIdx]]
        print("\nRide mode switched to: " + str(self.rideMode))
        
        # Update center LED to indicate ride mode
        self.lights["M"].colors[self.rideMode["color"]]()
        
        
    # Test LED functionality and Pin correctness
    def lightTest(self):
        # Blink each light
        for pin in self.lights:
            # Skip RGB pin
            if pin == 'M':
                continue
            print("Blinking light: " + str(pin))
            self.lights[pin].toggle()
            time.sleep(0.5)
            self.lights[pin].toggle()
        
        # Test RGB LED
        self.lights['M'].test()
        
            
    # Compute acceleration values
    def pollAcceleration(self):
        # Free unused memory
        gc.collect()
        
        accelOffset = 16384 # From LSB to g
        gyroOffset = 32.8   # From LSB to g
        
        self.imu.GyroAccelRead()
    
        self.ax = icm20948.Accel[0] / accelOffset # Longitudinal Acceleration
        self.ay = icm20948.Accel[1] / accelOffset # Lateral Acceleration 
        self.az = icm20948.Accel[2] / accelOffset # Vertical acceleration
        
        self.pitch = icm20948.Gyro[0] / gyroOffset # Pitch (deg/sec)
        self.roll = icm20948.Gyro[1] / gyroOffset # Roll (deg/sec)
        self.yaw = icm20948.Gyro[2] / gyroOffset # Yaw (deg/sec)
        
        
        
    # Flash all LEDs in the direction in which it is exceeding
    # 1.25x the tolerance
    def flashWarning(self, side, delay):
        numBlinks = 2
        
        # Minor error checking
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
        
        self.cleanup(clearAll=False)
                
    # Handle button press for data logger
    def handleLoggerBtn(self):
        press_start = time.time()
        
        # Toggle logging LED and update logger state
        self.enableLogger = not self.enableLogger
        
        # Check logger status
        if self.enableLogger:
            self.lights["logger"].value(1)
            print("\nData Logger started!")
        else:
            self.lights["logger"].value(0)
            print("\nData Logger terminated!")
            
        # Check if button is being held down
        while self.btnStartLogger.value() == 0:
            # Do nothing
            continue
                
        
    # Light up leds relative to acceleration
    # latTolerance = lateral g's per led
    # longTolF = longitudinal g's per front led
    # longTolR = longitudinal g's per rear led
    def monitor(self):
        print("\nMonitoring...")
        
        print("Current Ride mode: " + str(self.rideMode))
        
        try:
            while True:
                # Check for ride-mode button press
                if self.btnModeSel.value() == 0:
                    # Set callback behavior for mode select button
                    self.btnModeSel.irq(self.nextRideMode())
                    time.sleep(0.5)
                    
                
                # Check for startLogger button press
                if self.btnStartLogger.value() == 0:
                    # Set button call back to toggle logger
                    self.btnStartLogger.irq(self.handleLoggerBtn())
                    
                    
                
                # Set center LED to indicate ride mode
                self.lights["M"].colors[self.rideMode["color"]]()
                
                # Get current acceleration forces
                self.pollAcceleration()
                
                # Set tolerances
                latTolerance = self.rideMode['latTolerance']
                longTolF = self.rideMode['longTolF']
                longTolR = self.rideMode['longTolR']

                
                # Compute time delay
                delay = 1 / self.pollRateHz
                
                # Check lateral acceleration
                if self.ax > latTolerance or self.ax < -latTolerance:
                    # Check direction
                    if self.ax < 0:
                        # Right
                        numLeds = round(abs(self.ax / latTolerance))
                        
                        # Approaching slip angle
                        if self.ax <= -(self.maxLatForce - 0.1):
                            warningDelay = 0.1 / abs(self.ax/latTolerance)
                            
                            # Flash warning
                            self.flashWarning("right", warningDelay)
                            
                        else:
                            if numLeds == 1:
                                self.lights["1R"].toggle()
                                time.sleep(delay)
                                self.lights["1R"].toggle()
                            elif numLeds >= 2:
                                self.lights["1R"].toggle()
                                self.lights['2R'].toggle()
                                time.sleep(delay)
                                self.lights['1R'].toggle()
                                self.lights['2R'].toggle()
                            
                        
                        
                    # Left
                    else: 
                        numLeds = round(abs(self.ax / latTolerance))
                        
                        # Approaching slip angle
                        if self.ax >= self.maxLatForce - 0.1:
                            warningDelay = 0.1 / abs(self.ax/latTolerance)
                            
                            # Flash warning
                            self.flashWarning("left", warningDelay)
                        else:
                            if numLeds == 1:
                                self.lights["1L"].toggle()
                                time.sleep(delay)
                                self.lights["1L"].toggle()
                            elif numLeds >= 2:
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
                    elif numLeds >= 2:
                        self.lights["1D"].toggle()
                        self.lights['2D'].toggle()
                        time.sleep(delay)
                        self.lights['1D'].toggle()
                        self.lights['2D'].toggle()
                        
                # Braking
                elif self.ay <= 0:
                    numLeds = round(abs(self.ay/longTolF))
                    
                    if numLeds == 1:
                        self.lights["1U"].toggle()
                        time.sleep(delay)
                        self.lights["1U"].toggle()
                    elif numLeds >= 2:
                        self.lights["1U"].toggle()
                        self.lights['2U'].toggle()
                        time.sleep(delay)
                        self.lights['1U'].toggle()
                        self.lights['2U'].toggle()
                    
        
                        
            # Reset middle LED
            self.lights["M"].clear()

        except Exception as e:
            self.cleanup()
            print(e)
            
            
    # Free system resources and disable all GPIO
    def cleanup(self, clearAll=True):
        # Disable all GPIO
        for pin in self.lights:
            # Check if pin is rgb led
            if pin == "M":
                self.lights[pin].clear()
                continue
            
            # Check if logger pin and clear all
            if pin == "logger" and clearAll:
                self.lights[pin].value(0)
                continue
            else:
                continue
            
            self.lights[pin].value(0)
        
        # Free memory
        if clearAll:
            del(self.time_points)
            
            
    # Print system info to console
    def printInfo(self):
        print("\n\nGMonitor System Information:")
        print("=======================================")
        print("IMU Poll Rate: " + str(self.pollRateHz) + " Hz")
        print("Ride Mode: " + str(self.rideMode))
        
            
    """
    Getters and Setters
    """
    def setRideMode(self, mode):
        # Check if mode is valid
        if not mode in self.modes:
            print("Error in setRideMode(): invalid mode")
            return
        else:
            self.rideMode = self.modes[mode]
                
    def setPollRateHz(self, pollRate):
        self.pollRateHz = pollRate
                
def main():
    
     # Initialize gforce monitor
    gfm = GMonitor()
    
    # Start monitoring forces
    gfm.monitor()
    
    
    
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        gfm = GMonitor()
        gfm.cleanup()
