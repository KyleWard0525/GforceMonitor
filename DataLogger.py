"""
This is file contains classes and functions
for support the initial version of the data logger

Significant updates to this system are planned for the future
but this is a prototype for testing and learning.

kward
"""

import time
import json

# Data Logger Class
class Logger:
    
    # Initialize logger
    def __init__(self, gmonitor):
        # Validate monitor
        if not gmonitor:
            print("\nERROR in Logger.__init__(): gmonitor must not be null")
        
        # Set class variables
        self.monitor = gmonitor
        self.metrics = {} # Data metrics to store
        self.max_size = 10000000 # 10MB
        self.active = False
        
    # Compute and store metrics in structure
    def computeMetrics(self):
        if not self.active:
            self.active = True
        
        metrics = {}
        
        # Time point
        metrics['time'] = ((time.time_ns() - self.monitor.start_time) / 1000000.0)
        
        if metrics['time'] > 1000.0:
            metrics['time'] /= 1000.0
        
        # Acceleration
        metrics['longAccel'] = [self.monitor.ax, 'g']
        metrics['latAccel'] = [self.monitor.ay, 'g']
        metrics['vertAccel'] = [self.monitor.az, 'g']
        
        # Gyroscopic forces
        metrics['pitch'] = [self.monitor.pitch, 'deg/sec']
        metrics['yaw'] = [self.monitor.yaw, 'deg/sec']
        metrics['roll'] = [self.monitor.roll, 'deg/sec']
        
        # Derivative forces
        if metrics['latAccel'][0] == 0:
            metrics['rollPerLatAccel'] = 0.0
        else:
            metrics['rollPerLatAccel'] = [metrics['roll'][0]/metrics['latAccel'][0], 'deg/g'] 
        
        # Add instantaneous values to metrics structure
        self.metrics[len(self.metrics) + 1] = metrics
        
    
    # Save metrics to file
    def saveMetrics(self):
        file = open('log.txt', 'a') # Write in binary mode
        file.write(json.dumps(self.metrics))
        file.write("\n")
        file.close()
        self.metrics.clear()
        self.active = False
        
           
