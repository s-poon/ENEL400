
import RPi.GPIO as GPIO
import time

class zMotor:

    CCWStep = (0x01,0x02,0x04,0x08)                                                 # define power supply order for rotating anticlockwise 
    CWStep = (0x08,0x04,0x02,0x01) 
    ms = 3

    def __init__(self, pins):
        # GPIO.setmode(GPIO.BCM)
        self.pins = pins
        
        for i in range(len(pins)):
            GPIO.setup(pins[i], GPIO.OUT)

    def penUp(self):
        self.moveSteps(1, 32)
        self.motorStop()

    def penDown(self):
        self.moveSteps(0, 32)
        self.motorStop()
        
    def moveOnePeriod(self, dir):
        for j in range(0, 4):
            for i in range(0, 4):
                if(dir == 1):
                    GPIO.output(
                        self.pins[i],
                        ((self.CCWStep[j] == 1<<i) and GPIO.HIGH or GPIO.LOW)
                    )
                else:
                    GPIO.output(
                        self.pins[i],
                        (self.CWStep[j] == 1<<i) and GPIO.HIGH or GPIO.LOW
                    )
                time.sleep(self.ms*0.001)
    
    def moveSteps(self, dir, steps):
        for i in range(steps):
            self.moveOnePeriod(dir)

    def motorStop(self):
        for i in range(self.pins):
            GPIO.output(self.pins[i], GPIO.LOW)

