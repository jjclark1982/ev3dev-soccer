#!/usr/bin/env python3

from ev3dev2.motor import LargeMotor, OUTPUT_B, OUTPUT_C, SpeedPercent, MoveTank
from ev3dev2.sensor import Sensor, INPUT_4
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.led import Leds

import time

leds = Leds()

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


while True:
    if ir.value() < 5:
        tank_drive.on(SpeedPercent(75), SpeedPercent(25))
    elif ir.value() > 5:
        tank_drive.on(SpeedPercent(25), SpeedPercent(75))
    else:
        # in this case, ir.value() must be 5
        tank_drive.on(100,100)
    time.sleep(0.1)


