import RPi.GPIO as GPIO
import MotorControl
from StepperMotorClass import StepperMotor
import time
import math
import sys

GPIO.setmode(GPIO.BCM)

motorX = StepperMotor(21, 20)


try:
    while True:
        motorX.move(0, 20)
        print('motor is working')

except KeyboardInterrupt:
    GPIO.cleanup()
    exit()
