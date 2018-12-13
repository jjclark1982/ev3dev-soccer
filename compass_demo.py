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


def start():
    pass

def stop():
    tank_drive.on(0,0)

def update():
    find_north()


if __name__ == "__main__":
    while True:
        align_shot()
