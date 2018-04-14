#!/usr/bin/env python3

import wpilib
from wpilib.drive import DifferentialDrive
import robotuser

# user's vocal complaints about he speed they are traviling 
user_complaints = ['This is so slow!', 'I\'m good', 'Way too fast!']


class MyRobot(wpilib.SampleRobot):
    
    def robotInit(self):
        '''Robot initialization function'''
        self.person = robotuser.RobotUser()
        self.accel = wpilib.BuiltInAccelerometer(1)
        
        self.joystickChannel = 0  # usb number in DriverStation

        # channels for motors
        self.leftMotorChannel = 1
        self.rightMotorChannel = 0
        self.leftRearMotorChannel = 3
        self.rightRearMotorChannel = 2

        self.left = wpilib.SpeedControllerGroup(wpilib.Talon(self.leftMotorChannel),
                                                wpilib.Talon(self.leftRearMotorChannel))
        self.right = wpilib.SpeedControllerGroup(wpilib.Talon(self.rightMotorChannel),
                                                 wpilib.Talon(self.rightRearMotorChannel))
        self.myRobot = DifferentialDrive(self.left, self.right)

        self.joystick = wpilib.Joystick(self.joystickChannel)

    # autonomous means that we let our 'fake' user take control of the joystick 
    def autonomous(self):
        timer = wpilib.Timer()
        timer.start()
        i = 1
        (joy_y, joy_x) = (0,0)
        while self.isAutonomous() and self.isEnabled():
            (joy_y, joy_x, comment) = self.person.get_response(i,(-joy_y, -joy_x))
            i+=1
            if joy_y <= 0:
                # forwards
                joy_x = -joy_x
                self.myRobot.arcadeDrive(joy_y, joy_x)
            elif joy_y > 0:
                # backwards
                self.myRobot.arcadeDrive(joy_y, joy_x)
            print("Linear velocity = {}, Rotational = {}, Comment = {}".format(-joy_y,-joy_x,user_complaints[comment+1]), flush=True)
            
            wpilib.Timer.delay(1.0/30.0) # update at 30 fps

    # operatorControl means that we test the joystick ourselves. A joystick and be plugged 
    # into the USB port for testing 
    def operatorControl(self):
        
        while self.isOperatorControl() and self.isEnabled():
            joy_x = self.joystick.getX()
            joy_y = self.joystick.getY()
            if joy_y <= 0:
                # forwards
                joy_x = -joy_x
                self.myRobot.arcadeDrive(joy_y, joy_x)
            elif joy_y > 0:
                # backwards
                self.myRobot.arcadeDrive(joy_y, joy_x)
            print("Linear velocity = {}, Rotational = {}".format(-joy_y,-joy_x), flush=True)
            wpilib.Timer.delay(1.0/30.0) # update at 30 fps

    def test(self):
        '''Runs during test mode'''
        pass


if __name__ == "__main__":
    wpilib.run(MyRobot)
