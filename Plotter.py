
import xdrlib
import RPi.GPIO as GPIO
import MotorControl
from StepperMotorClass import StepperMotor
from zMotorClass import zMotor
import time
from math import pi, sin, cos, sqrt, acos, asin
import sys


class Test:
    # Pin declarations
    switchX  = 25
    switchY = 24
    xStep = 20
    xDir = 21
    yStep = 16
    yDir = 12
    zMotorPins = (6, 13, 19, 26)

    # Variables
    dx = 0.02
    dy = 0.02


    def setup(self):
        GPIO.setmode(GPIO.BCM)

        self.motorX = StepperMotor(self.xStep, self.xDir)
        self.motorY = StepperMotor(self.yStep, self.yDir)
        self.motorZ = zMotor(self.zMotorPins)
        GPIO.setup(self.switchX, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(self.switchY, GPIO.IN, pull_up_down = GPIO.PUD_UP)

        # print('Calibrating X-Axis')
        # while GPIO.input(self.switchX):
        #     self.motorX.move(0, 1)
        # print('Calibrated X-Axis')

        # print('Calibrating Y-Axis')
        # while GPIO.input(self.switchY):
        #     self.motorY.move(1, 1)
        # print('Calibrated Y-Axis')

    def XYposition(lines):
        # given a movement command line, return the X Y position
        xCharLoc = lines.index('X')
        i = xCharLoc + 1
        while (47 < ord(lines[i]) < 58) | (lines[i] == '.') | (lines[i] == '-'):
            i += 1
        xPos = float(lines[xCharLoc+1 : i])

        yCharLoc = lines.index('Y')
        i = yCharLoc+1
        while (47 < ord(lines[i]) < 58) | (lines[i] == '.') | (lines[i] == '-'):
            i += 1
        yPos = float(lines[yCharLoc+1 : i])

        return xPos, yPos

    def IJposition(lines):
        # given a G02 or G03 movement command line, return the I J position
        iCharLoc = lines.index('I')
        i = iCharLoc + 1
        while (47 < ord(lines[i]) < 58) | (lines[i] == '.') | (lines[i] == '-'):
            i += 1
        iPos = float(lines[iCharLoc+1 : i])

        jchar_loc = lines.index('J')
        i = jchar_loc+1
        while (47 < ord(lines[i]) < 58) | (lines[i] == '.') | (lines[i] == '-'):
            i += 1
        jPos = float(lines[jchar_loc+1 : i])

        return iPos, jPos

    def moveTo(xMotor, xPos, dx, yMotor, yPos, dy):
        # Move to (x_pos,y_pos) (in real unit)
        stepX = int(round(xPos/dx)) - xMotor.position
        stepY = int(round(yPos/dy)) - yMotor.position

        print('Movement: Dx=', stepX, '  Dy=', stepY)
        MotorControl.motorStep(xMotor, stepX, yMotor, stepY)

        return 0

    def testZ(self):
        while True:
            self.motorZ.penUp()
            time.sleep(2)
            self.motorZ.penDown()
            time.sleep(2)

        
    def readFile(self):
        if len(sys.argv) > 1:
            self.filename = str(sys.argv[1])

    def executeFile(self):
        self.motorZ.penUp()
        for lines in open('puppy_0001.nc', 'r'):
            print(lines)

            if lines == []:
                1
            
            elif lines[0:3] == 'G90':
                print('Starting')
            
            elif lines[0:3] == 'G21':  # working in mm
                print('Working in mm')
            
            elif lines[0:3] == 'M05':
                self.motorZ.penUp()

            elif lines[0:3] == 'M03':
                self.motorZ.penDown()

            elif lines[0:3] == 'M02':
                self.motorZ.penUp()
                print('finished. shuting down')
                break

            elif (lines[0:3] == 'G1F') | (lines[0:4] == 'G1 F'):
                1
            
            elif (lines[0:5] == 'G01 Z'):
                self.motorZ.penDown()

            elif (lines[0:5] == 'G00 Z'):
                self.motorZ.penUp()

            elif (    (lines[0:3] == 'G0 ') 
                    | (lines[0:3] == 'G1 ') 
                    | (lines[0:3] == 'G00') 
                    | (lines[0:3] == 'G01')
            ):
                # linear engraving movement
                if (lines[0:3] == 'G0 ' or lines[0:3] == 'G00'):
                    self.motorZ.penUp()
                else:
                    self.motorZ.penDown()

                if (lines.find('X') != -1 and lines.find('Y') != -1):
                    [xPos, yPos] = Test.XYposition(lines)
                    Test.moveTo(
                                self.motorX,
                                xPos, 
                                self.dx, 
                                self.motorY, 
                                yPos, 
                                self.dy
                    )

            elif (lines[0:3] == 'G02') | (lines[0:3] == 'G03'):  # circular interpolation
                if (lines.find('X') != -1 
                    and lines.find('Y') != -1 
                    and lines.find('I') != -1 
                    and lines.find('J') != -1
                ):

                    self.motorZ.penDown()

                    oldXPos = xPos
                    oldYPos = yPos

                    [xPos, yPos] = Test.XYposition(lines)
                    [iPos, jPos] = Test.IJposition(lines)

                    xcenter = oldXPos + iPos  # center of the circle for interpolation
                    ycenter = oldYPos + jPos

                    Dx = xPos - xcenter
                    # vector [Dx,Dy] points from the circle center to the new position
                    Dy = yPos - ycenter

                    r = sqrt(iPos**2 + jPos**2)   # radius of the circle

                    # pointing from center to current position
                    e1 = [-iPos, - jPos]
                    if (lines[0:3] == 'G02'):  # clockwise
                        # perpendicular to e1. e2 and e1 forms x-y system (clockwise)
                        e2 = [e1[1], -e1[0]]
                    else:  # counterclockwise
                        # perpendicular to e1. e1 and e2 forms x-y system (counterclockwise)
                        e2 = [-e1[1], e1[0]]

                    # [Dx,Dy]=e1*cos(theta)+e2*sin(theta), theta is the open angle

                    costheta = (Dx*e1[0] + Dy*e1[1])/r**2
                    # theta is the angule spanned by the circular interpolation curve
                    sintheta = (Dx*e2[0] +Dy*e2[1])/r**2

                    # there will always be some numerical errors! Make sure abs(costheta)<=1
                    if costheta > 1:
                        costheta = 1
                    elif costheta < -1:
                        costheta = -1

                    theta = acos(costheta)
                    if sintheta < 0:
                        theta = 2.0*pi - theta

                    # number of point for the circular interpolation
                    numStep = int(round(r*theta/self.dx/5.0))

                    for i in range(1, numStep + 1):
                        tmpTheta = i*theta/numStep
                        tempXPos = xcenter + e1[0] * \
                            cos(tmpTheta) + e2[0]*sin(tmpTheta)
                        tmpYPos = ycenter + e1[1] * \
                            cos(tmpTheta) + e2[1]*sin(tmpTheta)
                        Test.moveTo(
                            self.motorX, 
                            tempXPos, 
                            self.dx, 
                            self.motorY, 
                            tmpYPos, 
                            self.dy
                        )



    


# 0.04mm per step

if __name__ == '__main__':
    try:
        print('Initializing Program')
        thing = Test()
        thing.setup()
        print('Initialization is Complete')
        thing.readFile()
        thing.executeFile()
        thing.testZ()

    except KeyboardInterrupt:
        GPIO.cleanup()
        exit()
