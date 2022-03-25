import RPi.GPIO as GPIO
import MotorControl
from StepperMotorClass import StepperMotor
import time
import math
import sys

GPIO.setmode(GPIO.BCM)

motorX = StepperMotor(21, 20)
motorY = StepperMotor(19, 26)
switchX  = 25
switchY = 24


# 0.04mm per step

try:
    while True:
        # motorX.move(0, 200)
        MotorControl.motorStep(motorX, 200, motorY, 0)
        MotorControl.motorStep(motorX, 0, motorY, 200)
        MotorControl.motorStep(motorX, -200, motorY, 0)
        MotorControl.motorStep(motorX, 0, motorY, -200)
        time.sleep(2)
        print('motor is working')

except KeyboardInterrupt:
    GPIO.cleanup()
    exit()
