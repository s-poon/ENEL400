import RPi.GPIO as GPIO
import MotorControl
from StepperMotorClass import StepperMotor
import time
import math
import sys

GPIO.setmode(GPIO.BOARD)

motorX = StepperMotor(21, 20)


try:
    while True:
        motorX.move(1, 200)
        print('motor is working')

except KeyboardInterrupt:
    GPIO.cleanup()
    exit()
