
import RPi.GPIO as GPIO
import time

class StepperMotor:

    delayTime = 0.05
    stepsPerRev = 200

    def __init__(self, stepPin, dirPin):
        
        GPIO.setmode(GPIO.BCM)

        self.stepPin = stepPin
        self.dirPin = dirPin


        GPIO.setup(self.stepPin, GPIO.OUT)
        GPIO.setup(self.dirPin, GPIO.OUT)




    def move(self, dir, steps):
        multiplier = 1
        GPIO.output(self.dirPin, dir)
        for _ in range(steps):
            GPIO.output(self.stepPin, 1)
            time.sleep(1/1000)
            GPIO.output(self.stepPin, 0)
            time.sleep(1/1000)
    
    def unhold(self):
        GPIO.output(self.stepPin, 0)
