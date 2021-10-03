"""
This is file contains classes and functions
for support the initial version of the data logger

Significant updates to this system are planned for the future
but this is a prototype for testing and learning.

kward
"""

import time

# Data Logger Class
class Logger:
    
    # Initialize logger
    def __init__(self, gmonitor, pollRateHz=100):
        # Validate monitor
        if not gmonitor:
            print("\nERROR in Logger.__init__(): gmonitor must not be null")
        
        # Set class variables
        self.monitor = gmonitor
        self.delay = pollRateHz / 1000.0 # 10ms (with default)
        self.metrics = {} # Data metrics to store
        self.max_file_size = 10000000 # 10MB
        self.filename = 'log.txt'
        self.file = open(self.filename, "wb") # Write in binary mode
        self.active = True
        
        
    # Compute and store metrics in structure
    def computeMetrics(self):
        # Poll values from monitor
        self.monitor.pollAcceleration()
        
        # Time point
        self.metrics['time'] = (time.time() - self.monitor.start_time)
        
        # Acceleration
        self.metrics['longAccel'] = [self.monitor.ax, 'g']
        self.metrics['latAccel'] = [self.monitor.ay, 'g']
        self.metrics['vertAccel'] = [self.monitor.az, 'g']
        
        # Gyroscopic forces
        self.metrics['pitch'] = [self.monitor.pitch, 'deg/sec']
        self.metrics['yaw'] = [self.monitor.yaw, 'deg/sec']
        self.metrics['roll'] = [self.monitor.roll, 'deg/sec']
        
        # Derivative forces
        self.metrics['rollPerLatAccel'] = [self.metrics['roll'][0]/self.metrics['latAccel'][0], 'deg/g'] 
        
        print("\n" + str(self.metrics))
        
    
    # Start the data logger
    def start(self):
        # Check if file is open
        if self.file.closed():
            self.file = open(self.filename, 'wb')
            
        # Run while logger is active
        while self.active:
            pass
        
    
    
    # Turn off data logger
    def stop(self, saveData=False):
        # Check if current metrics should be saved to file
        if not saveData:
            self.active = False
        else:
            # TODO: Add logic to save metrics
            self.saveMetrics()
            self.file.close()
        
    # Save metrics to file
    def saveMetrics(self):
        self.file.write(self.metrics)
    
    # Set poll rate of logger in hertz
    def setPollRateHz(self, pollRate):
        self.delay = pollRate / 1000.0
        
    # Get compute delay in ms
    def printDelay(self):
        print("\nCurrent Logger delay %.2fms" % self.delay)
            
    
