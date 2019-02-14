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

tank_drive = MoveTank(OUTPUT_B, OUTPUT_C)
steer_drive = MoveSteering(OUTPUT_B, OUTPUT_C)
leds = Leds()


# Define Functions

def calibrate_gyro():
    tank_drive.on(0,0)
    time.sleep(0.1)
    gyro.mode = 'GYRO-CAL'
    time.sleep(0.1)
    gyro.mode = 'GYRO-ANG'

def calibrate_compass():
    tank_drive.on(0,0)
    time.sleep(0.1)
    compass.command = 'BEGIN-CAL'
    steer_drive.on(100, SpeedPercent(75))
    while (gyro.value() < 360):
        time.sleep(0.1)
    tank_drive.on(0,0)
    compass.command = 'END-CAL'

def strike(target=5):
    if ir.value() == 0:
        tank_drive.on(0,0)
    elif ir.value() < target:
        # turn right
        d = target - ir.value() # 0 to 5
        steer_drive.on(15*d, SpeedPercent(75))
    elif ir.value() > target:
        # turn left
        d = target - ir.value() # 0 to -5
        steer_drive.on(15*d, SpeedPercent(75))
    else:
        steer_drive.on(0, SpeedPercent(100))

last_known_dir = 0
def get_angle_to_ball(ir_value):
    global last_known_dir
    if ir_value == 0:
        return None
    angle = (5 - ir_value)*30
    last_known_dir = angle
    return angle

last_color_seen = 0 # black
def get_angle_to_goal(gyro_value):
    global last_color_seen
    green = color_sensor.rgb[1]

    if green > 150: # white
        green = last_color_seen
    else:
        last_color_seen = green

    if green > 128: # light green
        gyro_value += 30.0
    elif green > 64: # medium green
        gyro_value += -30.0
    elif green > 28: # dark green
        pass
    else: # black
        pass
    gyro_angle = -((gyro_value + 180) % 360 - 180)
    return gyro_angle   

def align_shot():
    angle_to_goal = get_angle_to_goal(gyro.value())
    angle_to_ball = get_angle_to_ball(ir.value())
    print("goal: {}, ball: {}, compass: {}, color: {}".format(
        angle_to_goal, angle_to_ball, compass.value(), color_sensor.rgb))
    if angle_to_ball is None:
        if last_known_dir > 60:
            steer_drive(100, SpeedPercent(40))
        elif last_known_dir < -60:
            steer_drive(-100, SpeedPercent(40))
        else:
            tank_drive.on(0,0)
    elif abs(angle_to_goal - angle_to_ball) < 5:
        print("striking")
        strike(5)
    elif angle_to_goal < angle_to_ball:
        strike(5.5)
    else:
        strike(4.5)

# Lifecycle Handlers

def start():
    calibrate_gyro()
    calibrate_compass()

def stop():
    # stop motors when program exits
    tank_drive.on(0,0)

def update():
    align_shot()

# Main Program

if __name__ == "__main__":
    atexit.register(stop)
    start()
    while True:
        update()
