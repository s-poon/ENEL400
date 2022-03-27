import xdrlib
import RPi.GPIO as GPIO
import MotorControl
from StepperMotorClass import StepperMotor
from zMotorClass import zMotor
import time
from math import pi, sin, cos, sqrt, acos, asin
import sys

# Pin declarations
switchX  = 25
switchY = 24
xStep = 20
xDir = 21
yStep = 16
yDir = 12
zMotorPins = (5, 6, 13, 19)

# Variables
dx = 0.04
dy = 0.04


def setup(self):
    GPIO.setmode(GPIO.BCM)

    self.motorX = StepperMotor(xStep, xDir)
    self.motorY = StepperMotor(yStep, yDir)
    self.motorZ = zMotor(zMotorPins)
    GPIO.setup(switchX, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(switchY, GPIO.IN, pull_up_down = GPIO.PUD_UP)

    print('Calibrating X-Axis')
    while not GPIO.input(switchX):
        self.motorX.move(1, 1)
    print('Calibrated X-Axis')

    print('Calibrating Y-Axis')
    while not GPIO.input(switchY):
        self.motorY.move(1, 1)
    print('Calibrated Y-Axis')

def XYposition(lines):
    # given a movement command line, return the X Y position
    xchar_loc = lines.index('X')
    i = xchar_loc+1
    while (47 < ord(lines[i]) < 58) | (lines[i] == '.') | (lines[i] == '-'):
        i += 1
    x_pos = float(lines[xchar_loc+1:i])

    ychar_loc = lines.index('Y')
    i = ychar_loc+1
    while (47 < ord(lines[i]) < 58) | (lines[i] == '.') | (lines[i] == '-'):
        i += 1
    y_pos = float(lines[ychar_loc+1:i])

    return x_pos, y_pos

def IJposition(lines):
    # given a G02 or G03 movement command line, return the I J position
    ichar_loc = lines.index('I')
    i = ichar_loc+1
    while (47 < ord(lines[i]) < 58) | (lines[i] == '.') | (lines[i] == '-'):
        i += 1
    i_pos = float(lines[ichar_loc+1:i])

    jchar_loc = lines.index('J')
    i = jchar_loc+1
    while (47 < ord(lines[i]) < 58) | (lines[i] == '.') | (lines[i] == '-'):
        i += 1
    j_pos = float(lines[jchar_loc+1:i])

    return i_pos, j_pos

def moveto(MX, x_pos, dx, MY, y_pos, dy):
    # Move to (x_pos,y_pos) (in real unit)
    stepx = int(round(x_pos/dx))-MX.position
    stepy = int(round(y_pos/dy))-MY.position

    print('Movement: Dx=', stepx, '  Dy=', stepy)
    MotorControl.motorStep(MX, stepx, MY, stepy)

    return 0
    
def readFile(self):
    if len(sys.argv) > 1:
        self.filename = str(sys.argv[1])

def executeFile(self):
    self.motorZ.penUp()
    for lines in open(self.filename, 'r'):
        print(lines)

        if lines == []:
            1
        
        elif lines[0:3] == 'G90':
            print('Starting')
        
        elif lines[0:3] == 'G21':  # working in mm
            print('Working in mm')
        
        elif lines[0:3] == 'M05':
            self.zMotor.penUp()

        elif lines[0:3] == 'M03':
            self.zMotor.penDown()

        elif lines[0:3] == 'M02':
            self.zMotor.penUp()
            print('finished. shuting down')
            break

        elif (lines[0:3] == 'G1F') | (lines[0:4] == 'G1 F'):
            1
        
        elif (lines[0:5] == 'G01 Z'):
            self.zMotor.penDown()

        elif (lines[0:5] == 'G00 Z'):
            self.zMotor.penUp()

        elif (lines[0:3] == 'G0 ') | (lines[0:3] == 'G1 ') | (lines[0:3] == 'G00') | (lines[0:3] == 'G01'):
            # linear engraving movement
            if (lines[0:3] == 'G0 ' or lines[0:3] == 'G00'):
                self.zMotor.penUp()
            else:
                self.zMotor.penDown()

            if (lines.find('X') != -1 and lines.find('Y') != -1):
                [x_pos, y_pos] = XYposition(lines)
                moveto(self.motorX, x_pos, dx, self.motorY, y_pos, dy)

        elif (lines[0:3] == 'G02') | (lines[0:3] == 'G03'):  # circular interpolation
            if (lines.find('X') != -1 and lines.find('Y') != -1 and lines.find('I') != -1 and lines.find('J') != -1):
                self.zMotor.penDown()

                old_x_pos = x_pos
                old_y_pos = y_pos

                [x_pos, y_pos] = XYposition(lines)
                [i_pos, j_pos] = IJposition(lines)

                xcenter = old_x_pos+i_pos  # center of the circle for interpolation
                ycenter = old_y_pos+j_pos

                Dx = x_pos-xcenter
                # vector [Dx,Dy] points from the circle center to the new position
                Dy = y_pos-ycenter

                r = sqrt(i_pos**2+j_pos**2)   # radius of the circle

                # pointing from center to current position
                e1 = [-i_pos, -j_pos]
                if (lines[0:3] == 'G02'):  # clockwise
                    # perpendicular to e1. e2 and e1 forms x-y system (clockwise)
                    e2 = [e1[1], -e1[0]]
                else:  # counterclockwise
                    # perpendicular to e1. e1 and e2 forms x-y system (counterclockwise)
                    e2 = [-e1[1], e1[0]]

                # [Dx,Dy]=e1*cos(theta)+e2*sin(theta), theta is the open angle

                costheta = (Dx*e1[0]+Dy*e1[1])/r**2
                # theta is the angule spanned by the circular interpolation curve
                sintheta = (Dx*e2[0]+Dy*e2[1])/r**2

                # there will always be some numerical errors! Make sure abs(costheta)<=1
                if costheta > 1:
                    costheta = 1
                elif costheta < -1:
                    costheta = -1

                theta = acos(costheta)
                if sintheta < 0:
                    theta = 2.0*pi-theta

                # number of point for the circular interpolation
                no_step = int(round(r*theta/dx/5.0))

                for i in range(1, no_step+1):
                    tmp_theta = i*theta/no_step
                    tmp_x_pos = xcenter+e1[0] * \
                        cos(tmp_theta)+e2[0]*sin(tmp_theta)
                    tmp_y_pos = ycenter+e1[1] * \
                        cos(tmp_theta)+e2[1]*sin(tmp_theta)
                    moveto(self.motorX, tmp_x_pos, dx, self.motorY, tmp_y_pos, dy)



    


# 0.04mm per step

if __name__ == '__main__':
    print('Initializing Program')
    setup()
    print('Initialization is Complete')
    try:
        readFile()
        executeFile()

    except KeyboardInterrupt:
        GPIO.cleanup()
        exit()
