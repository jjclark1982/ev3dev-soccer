#!/usr/bin/env python3

from ev3dev2.motor import LargeMotor, OUTPUT_B, OUTPUT_C, SpeedPercent, MoveTank, MoveSteering
from ev3dev2.sensor import Sensor, list_sensors
from ev3dev2.sensor.lego import TouchSensor, GyroSensor, ColorSensor
from ev3dev2.led import Leds
import time
import atexit

# Set Up Devices

for s in list_sensors():
    if s.driver_name == 'ht-nxt-compass':
        compass = s
    elif s.driver_name == 'lego-ev3-gyro':
        gyro = GyroSensor(s.address)
    elif s.driver_name == 'ht-nxt-ir-seek-v2':
        ir = s
    elif s.driver_name == 'lego-ev3-color':
        color_sensor = ColorSensor(s.address)
    elif s.driver_name == 'lego-ev3-us':
        sonic = s

tank_drive = MoveTank(OUTPUT_B, OUTPUT_C)
steer_drive = MoveSteering(OUTPUT_B, OUTPUT_C)
leds = Leds()


def stop():
    # stop motors when program exits
    tank_drive.on(0,0)


steering_amount = 50

def update():
    global steering_amount
    steering_amount = steering_amount * 0.999
    print(steering_amount)
    steer_drive.on(steering_amount, 50)
