
import time
from StepperMotorClass import StepperMotor
from math import sqrt

def GCD(a, b):  # greatest common diviser
    while b:
        a, b = b, a % b
    return a


def LCM(a, b): # least common multipler
    return a*b/GCD(a, b)

def sign(a):  # return the sign of number a
    if a > 0:
        return 1
    elif a < 0:
        return 0
    else:
        return 0

def motorStep(stepper1, step1, stepper2, step2):
    
    dir1 = sign(step1)
    dir2 = sign(step2)

    step1 = abs(step1)
    step2 = abs(step2)

    if step1 == 0:
        totalMicroSteps = step2
        microStep2 = 1
        microStep1 = step2 + 100
    elif step2 == 0:
        totalMicroSteps = step1
        microStep1 = 1
        microStep2 = step1 + 100
    else:
        totalMicroSteps = LCM(step1, step2)
        microStep1 = totalMicroSteps/step1
        microStep2 = totalMicroSteps/step2
    
    for i in range(1, int(totalMicroSteps) + 1):
        if ((i % microStep1) == 0):
            stepper1.move(dir1, 1)
        
        if((i % microStep2) == 0):
            stepper2.move(dir2, 1)
        
    return 0