# G-Force Monitor
A device that utilizes LEDs to visualize the g-force one is experiencing. It is primarily being designed for use in vehicles that are often subjected to extreme forces, such as race cars.

The project is written in MicroPython, a condensed form of python capable of being run on the Raspberry Pi Pico.

# Hardware
- Waveshare 10-DOF Inertial Measurement Unit (IMU)
- Raspberry Pi Pico
- Breadboard
- Jumper Wires
- Basic Anode LEDs
- RGB LED
- Buttons

# Software
- The software is being written in Python using MicroPython for the RPi Pico

# How It Works
The hardware consist of 9 led's in a "+" shape. It also uses a Raspberry Pi Pico in combination with a Waveshare 10-DOF IMU
in order to measure acceleration on the X, Y, and Z axis. 


![MonitorDesign8-20-2021](https://user-images.githubusercontent.com/36857534/130289143-5bacec8d-2b7a-4185-a464-6a2ab940e75e.jpg)


When the device experiences lateral or longitudinal acceleration, it will begin to light up led's in the direction in 
which it is feeling the forces. It also includes a Z-axis (Center) LED which is used primarily as a status indicator but will eventually be updated 
to serve other roles as well.

Both the lateral and longitudinal axes have independently adjustable force tolerances for each LED. As of version 1.0, a global constant has been 
added to allow for tuning the maximum lateral force tolerance the vehicle can handle. This is typically dependent upon external factors such as weather,
road conditions, tire compound, tire size, aerodynamics, etc. but is currently a hard-coded average for more efficient development.

The device also includes a primitive tire slip warning sensor that will cause the led's experiencing g-forces to flash urgently to 
warn the user that their tires are about to slip as they are approaching the maximum lateral force tolerance. 

# Updates

  ## v1.1
   - *Added support for different ride modes. Each ride mode changes the lateral, forward, and braking force tolerances
   of their respective LEDs. This allows the user to change the configuration of the monitor to best suit how they want to
   drive, in realtime!*
   
   - *Center (Z-axis) RGB LED now supports visualizing different ride modes based on their color*
 
   - *A button has been added to the circuit to allow the user to change the current ride mode*

                


# Upcoming features (potentially)
- Data logger
- Add additional LEDs and functions to allow for a tire-slip warning as well as a spinout warning
- Generalize for easier tuning for any type of vehicle
- Digitalize and roll into a large vehicle telemetry project
