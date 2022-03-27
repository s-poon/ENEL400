
import RPi.GPIO as GPIO
import time

class StepperMotor:

    delayTime = 1/2000
    stepsPerRev = 200
    position = 0

    def __init__(self, stepPin, dirPin):
        
        self.stepPin = stepPin
        self.dirPin = dirPin

        GPIO.setmode(GPIO.BCM)
        
        GPIO.setup(self.stepPin, GPIO.OUT)
        GPIO.setup(self.dirPin, GPIO.OUT)
        self.position = 0

    def move(self, dir, steps):
        multiplier = 1
        GPIO.output(self.dirPin, dir)
        for _ in range(steps):
            GPIO.output(self.stepPin, 1)
            time.sleep(self.delayTime)
            GPIO.output(self.stepPin, 0)
            time.sleep(self.delayTime)
            if dir == 0:
                position -= 1
            else:
                position += 1
    
    def unhold(self):
        GPIO.output(self.stepPin, 0)