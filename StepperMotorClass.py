
import RPi.GPIO as GPIO
import time

class StepperMotor:

    delayTime = 1/2000
    stepsPerRev = 200

    def __init__(self, stepPin, dirPin):
        
        self.stepPin = stepPin
        self.dirPin = dirPin

        # GPIO.setmode(GPIO.BCM)
        
        GPIO.setup(self.stepPin, GPIO.OUT)
        GPIO.setup(self.dirPin, GPIO.OUT)




    def move(self, dir, steps):
        multiplier = 1
        GPIO.output(self.dirPin, dir)
        for _ in range(steps):
            GPIO.output(self.stepPin, 1)
            time.sleep(self.delayTime)
            GPIO.output(self.stepPin, 0)
            time.sleep(self.delayTime)
    
    def unhold(self):
        GPIO.output(self.stepPin, 0)
