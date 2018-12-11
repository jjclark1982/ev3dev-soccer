#!/usr/bin/env python3

from ev3dev2.motor import LargeMotor, OUTPUT_B, OUTPUT_C, SpeedPercent, MoveTank
from ev3dev2.sensor import Sensor, list_sensors
from ev3dev2.sensor.lego import TouchSensor, GyroSensor, ColorSensor
from ev3dev2.led import Leds
import time
import atexit
import json
from datetime import datetime, timedelta

# Set Up Devices

for s in list_sensors():
    if s.driver_name == 'ht-nxt-compass':
        compass = s
    elif s.driver_name == 'lego-ev3-gyro':
        gyro = GyroSensor(s.addres)
    elif s.driver_name == 'ht-nxt-ir-seek-v2':
        ir = s
    elif s.driver_name == 'lego-ev3-color':
        color_sensor = ColorSensor(s.address)

tank_drive = MoveTank(OUTPUT_B, OUTPUT_C)
leds = Leds()

config = {
    "strike_angle": 5,

    "curve_left_sector": 5.5,
    "curve_right_sector": 4.5,
    "curve_start": 75,
    "curve_delta": 25,

    "color_white": 150,
    "color_light_green": 128,
    "color_medium_green": 64,
    "color_dark_green": 28,
    "color_black": 0,

    "offset_light_green": 30.0,
    "offset_medium_green": -30.0
}
config_loaded_time = datetime.min # a long time ago

def load_config(self, filename="config.json"):
    global config, config_loaded_time
    if datetime.now() - config_loaded_time > timedelta(0,1): # one second
        config_loaded_time = datetime.now()
        try:
            with open(filename) as config_file:
                new_config = json.load(config_file)
                config.update(new_config)
        except Exception as e:
            print("Error loading config file:", e)

# stop motors when program exits
@atexit.register
def brake():
    tank_drive.on(0,0)


# Define Functions

def calibrate_gyro():
    brake()
    time.sleep(0.1)
    gyro.mode = 'GYRO-CAL'
    time.sleep(0.1)
    gyro.mode = 'GYRO-ANG'

def strike(target=5):
	if ir.value() == 0:
		tank_drive.on(0,0)
	elif ir.value() < target:
        # turn tighter when the angle to ball is larger
        left = config["curve_start"]
        right = config["curve_start"] - config["curve_delta"]*(target-ir.value())
		tank_drive.on(SpeedPercent(left), SpeedPercent(right))
	elif ir.value() > target:
        right = config["curve_start"]
        left = config["curve_start"] - config["curve_delta"]*(ir.value()-target)
        tank_drive.on(SpeedPercent(left), SpeedPercent(right))
	else:
		tank_drive.on(100,100)

def get_angle_to_ball(ir_value):
    if ir_value == 0:
        return None
    return (5 - ir_value)*30

last_color_seen = 0 # black
def get_angle_to_goal(gyro_value):
    global last_color_seen
    green = color_sensor.rgb[1]

    if green > config["color_white"]:
    	green = last_color_seen
    else:
        last_color_seen = green

    if green > config["color_light_green"]:
    	gyro_value += config["offset_light_green"]
    elif green > config["color_medium_green"]:
    	gyro_value += config["offset_medium_green"]
    else:
        pass
    gyro_angle = -((gyro_value + 180) % 360 - 180)
    return gyro_angle    	

def align_shot():
    angle_to_goal = get_angle_to_goal(gyro.value())
    angle_to_ball = get_angle_to_ball(ir.value())
    print("goal: {}, ball: {}, compass: {}, color: {}".format(
    	angle_to_goal, angle_to_ball, compass.value(), color_sensor.rgb))
    if angle_to_ball is None:
        brake()
    elif abs(angle_to_goal - angle_to_ball) < config["strike_angle"]:
        print("striking")
        strike(5)
    elif angle_to_goal < angle_to_ball:
        strike(config["curve_left_sector"])
    else:
        strike(config["curve_right_sector"])

# Main Program

if __name__ == "__main__":
    load_config()
    calibrate_gyro()
    while True:
        load_config()
        align_shot()
        time.sleep(0.01)


# TODO: automatically load configuration constants from a file
# and watch that file for changes
# https://stackoverflow.com/questions/3274334/how-can-i-watch-a-file-for-modification-change
