#!/usr/bin/env python3

from ev3dev2.motor import LargeMotor, OUTPUT_B, OUTPUT_C, SpeedPercent, MoveTank
from ev3dev2.sensor import Sensor, INPUT_4
from ev3dev2.sensor.lego import TouchSensor, GyroSensor
from ev3dev2.led import Leds
import ev3dev2.auto
import time

sensors = ev3dev2.auto.list_sensors()
for s in sensors:
    if s.driver_name == 'ht-nxt-compass':
        compass = s
    elif s.driver_name == 'lego-ev3-gyro':
        gyro = s
    elif s.driver_name == 'ht-nxt-ir-seek-v2':
        ir = s
    elif s.driver_name == 'lego-ev3-color':
        color = s


gyro.mode = 'GYRO-CAL'
time.sleep(0.1)
gyro.mode = 'GYRO-ANG'

leds = Leds()


#while True:
#    print("compass: {}, gyro: {}".format(compass.value(),gyro.value()))
#    time.sleep(0.1)

#while True:
#    leds.set_color("LEFT", "GREEN")
#    leds.set_color("RIGHT", "GREEN")
#    time.sleep(1)
#    leds.set_color("LEFT", "RED")
#    leds.set_color("RIGHT", "RED")
#    time.sleep(1)

ir = Sensor('in4:i2c8')

tank_drive = MoveTank(OUTPUT_B, OUTPUT_C)

# drive in a turn for 5 rotations of the outer motor
# the first two parameters can be unit classes or percentages.
#tank_drive.on_for_rotations(SpeedPercent(50), SpeedPercent(75), 10)

# drive in a different turn for 3 seconds
#tank_drive.on_for_seconds(SpeedPercent(60), SpeedPercent(30), 3)

def find_north():
    while True:
        print(compass.value())
        if compass.value() < 85:
            tank_drive.on(25,-25)
        elif compass.value() > 95:
            tank_drive.on(-25,25)
        else:
            tank_drive.on(0,0)
        time.sleep(0.1)







def strike():
        if ir.value() == 0:
            tank_drive.on(0,0)
        elif ir.value() < 5:
            tank_drive.on(SpeedPercent(75), SpeedPercent(25))
        elif ir.value() > 5:
            tank_drive.on(SpeedPercent(25), SpeedPercent(75))
        else:
            # in this case, ir.value() must be 5
            tank_drive.on(100,100)
        time.sleep(0.1)


def curve_left(angle_to_ball):
    if angle_to_ball < 15:
        tank_drive.on(75, 25)
    else:
        tank_drive.on(25, 75)

def curve_right(angle_to_ball):
    if angle_to_ball < -15:
        tank_drive.on(75, 25)
    else:
        tank_drive.on(25, 75)


def get_angle_to_ball(ir_value):
    if ir_value == 0:
        return None
    return (5 - ir_value)*15

def align_shot():
    angle_to_goal = -((gyro.value() + 180) % 360 - 180)
    angle_to_ball = get_angle_to_ball(ir.value())
    print("goal: {}, ball: {}, compass: {}".format(angle_to_goal, angle_to_ball, compass.value()))
    if angle_to_ball is None:
        tank_drive.on(0,0)
        return
    if abs(angle_to_goal - angle_to_ball) < 5:
        print("striking")
        strike()
    elif angle_to_goal < angle_to_ball:
        curve_left(angle_to_ball)
    else:
        curve_right(angle_to_ball)


if __name__ == "__main__":
    while True:
        align_shot()
