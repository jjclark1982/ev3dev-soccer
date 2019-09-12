#!/usr/bin/env python3

from ev3dev2.motor import LargeMotor, OUTPUT_B, OUTPUT_C, SpeedPercent, MoveTank, MoveSteering
from ev3dev2.sensor import Sensor, list_sensors
from ev3dev2.sensor.lego import TouchSensor, GyroSensor, ColorSensor
from ev3dev2.led import Leds
from ev3dev2.button import Button
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
buttons = Button()

# Define Functions

def calibrate_gyro():
    tank_drive.on(0,0)
    time.sleep(0.1)
    gyro.mode = 'GYRO-CAL'
    time.sleep(0.1)
    gyro.mode = 'GYRO-ANG'
    return "calibrate_compass"

def calibrate_compass():
    tank_drive.on(0,0)
    time.sleep(0.1)
    compass.command = 'BEGIN-CAL'
    steer_drive.on(100, SpeedPercent(75))
    while (gyro.value() < 360):
        time.sleep(0.1)
    tank_drive.on(0,0)
    compass.command = 'END-CAL'
    return "orient_toward_goal"

compass_dir_to_goal = None
def orient_toward_goal():
    global compass_dir_to_goal
    compass_dir_to_goal = compass.value()
    calibrate_gyro()
    return "look_for_ball"

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
    return "look_for_ball"

def strike_left():
    return strike(4.5)

def strike_right():
    return strike(5.5)

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

def remember_left():
    steer_drive.on(-100, SpeedPercent(40))
    return "look_for_ball"

def remember_right():
    steer_drive.on(100, SpeedPercent(40))
    return "look_for_ball"

def pause():
    steer_drive.off()
    return "pause"

def back_off():

    return "look_for_ball"

def look_for_ball():
    # angle_to_goal = get_angle_to_goal(gyro.value())
    angle_to_goal = get_angle_to_goal(compass.value() - compass_dir_to_goal)
    angle_to_ball = get_angle_to_ball(ir.value())
    print("goal: {}, gyro: {}, ball: {}, compass: {}, color: {} ".format(
        angle_to_goal, gyro.value(), angle_to_ball, compass.value(), color_sensor.rgb),
        end="", flush=True)
    if angle_to_ball is None:
        if last_known_dir > 60:
            return "remember_right"
        elif last_known_dir < -60:
          return "remember_left"
        else:
            tank_drive.on(0,0)
    elif abs(angle_to_goal - angle_to_ball) < 5:
        return "strike"
    elif angle_to_goal < angle_to_ball:
        return "strike_right"
    else:
        return "strike_left"
    return "look_for_ball"

override_handler = {
    "up": "orient_toward_goal",
    "down": "pause",
    "left": None,
    "right": None,
    "bump": "back_off"
}
state_handler = {
    "calibrate_gyro": (calibrate_gyro, "AMBER", "AMBER"),
    "calibrate_compass": (calibrate_compass, "AMBER", "AMBER"),
    "orient_toward_goal": (orient_toward_goal, "AMBER", "AMBER"),
    "look_for_ball": (look_for_ball, None, None),
    "strike": (strike, "GREEN", "GREEN"),
    "strike_left": (strike_left, "GREEN", (0,0)),
    "strike_right": (strike_right, (0,0), "GREEN"),
    "remember_left": (remember_left, "AMBER", (0,0)),
    "remember_right": (remember_right, (0,0), "AMBER"),
    "pause": (pause, (0,0), (0,0)),
    "back_off": (back_off, "RED", "RED")
}
current_state = "calibrate_gyro"

# Lifecycle Handlers


def stop():
    # stop motors when program exits
    tank_drive.on(0,0)

def update():
    global current_state

    if buttons.up:
        current_state = override_handler["up"]

    if buttons.down:
        current_state = override_handler["down"]

    print("Current state: "+current_state)
    handler = state_handler[current_state]
    if handler[1] is not None:
        leds.set_color('LEFT', handler[1])
    if handler[2] is not None:
        leds.set_color('RIGHT', handler[2])
    next_state = handler[0]()
    current_state = next_state

# Main Program

if __name__ == "__main__":
    atexit.register(stop)
    start()
    while True:
        update()
