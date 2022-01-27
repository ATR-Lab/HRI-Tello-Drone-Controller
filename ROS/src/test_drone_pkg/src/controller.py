#!/usr/bin/env python


# Default libraries from ROS for the project
import rospy
import math
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy
from std_msgs.msg import Empty


# Constant variables for drone position and joystick inputs
currentTwistX = 0 # Linear
currentTwistY = 0 # Linear
currentTwistZ = 0 # Linear
forwardValue = 0 # Speed
backwardsValue = 0 # Speed
steeringValue = 0 # Angular
heightValue = 0 # Linear
leanValue = 0 # Linear
joystickInput = [] # Inputs


# Similar to the map() function in Arduino C, used for analog inputs
def _map(x, in_min, in_max, out_min, out_max):
    return float((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def isClose(a, b, rel_tol=1e-9, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

# Send a Twist message to the drone, standard Twist message setup
def sendTwist(x = 0, y = 0, z = 0, ax = 0, ay = 0, az = 0):
    global currentTwistX
    global currentTwistY
    global currentTwistZ 

    joystickPub = rospy.Publisher('/tello/cmd_vel', Twist, queue_size=10)

    twist = Twist()

    currentTwistX = x
    currentTwistY = y
    currentTwistZ = z

    twist.linear.x = currentTwistX
    twist.linear.y = currentTwistY
    twist.linear.z = currentTwistZ 

    twist.angular.x = ax
    twist.angular.y = ay
    twist.angular.z = az

    joystickPub.publish(twist)


# Parsing the input for the drone
def parseInput(input):
    buttonResult = '' # Topic for the button press

    # Insert input option here that corresponds with drone topic
    if input == 'start':
        buttonResult = 'takeoff'
    elif input == 'select':
        buttonResult = 'land'
    elif input == 'home':
        buttonResult = 'emergency'
    elif input == 'x':
        buttonResult = 'flip'

    # Analog shoulder buttons for forward and backwards movement
    if input == 'r2':
        buttonResult = 'cmd_vel_forward'
    elif input == 'l2':
        buttonResult = 'cmd_vel_backwards'
    
    # Send button result to drone
    if not buttonResult == '' and not 'cmd_vel' in buttonResult:
        global buttonPub
        buttonPub = rospy.Publisher('/tello/' + buttonResult, Empty, queue_size=10)
        buttonPub.publish()

    # Twist forward and backwards speed
    elif 'cmd_vel' in buttonResult:
        if 'forward' in buttonResult:
            global forwardValue
            sendTwist(0, forwardValue, heightValue, 0, steeringValue, 0)
        elif 'backwards' in buttonResult:
            global backwardsValue
            sendTwist(0, backwardsValue, heightValue, 0, steeringValue, 0)


# Gather input from controller (For the Duelshock 3 PS3 controller)
def controllerCase(data):
    # Global variables for speed and height
    global steeringValue
    global heightValue
    global leanValue
    
    # Initial input and button layout in accordence to joy topic
    inputs = []
    buttons = ['x', 'o', 'square', 'triangle', 'l1', 'r1', 'l2', 'r2', 'select', 'start', 'home', 'l3', 'r3', 'up', 'down', 'left', 'right']

    # Enumerate through sent data, if any of them are sent high (1), add them to the input list
    for idx, val in enumerate(data.buttons):
        if val == 1:
            inputs.append(buttons[idx])

            # If they're analog triggers, have them set the value for the speed
            if buttons[idx] == 'r2':
                global forwardValue
                forwardValue = _map(data.axes[5], -1, 1, 2, 0)
            elif buttons[idx] == 'l2':
                global backwardsValue
                backwardsValue = _map(data.axes[2], -1, 1, -2, 0)

    # Set steering and height values from joystick input
    steeringValue = _map(data.axes[3], 1, -1, -2, 2)
    heightValue = _map(data.axes[4], -1, 1, -2, 2)
    leanValue = _map(data.axes[0], 1, -1, -2, 2)
    return inputs


def parseSteerInput(input):
    # Global variables for speed and height
    global heightValue
    global forwardValue
    global backwardsValue

    buttonResult = '' # Topic for the button press

    # Insert input option here that corresponds with drone topic
    if input == '3':
        buttonResult = 'takeoff'
    elif input == '2':
        buttonResult = 'land'
    elif input == 'HOME':
        buttonResult = 'emergency'
    elif input == 'UP':
        buttonResult = 'cmd_vel_forward'
    elif input == 'DOWN':
        buttonResult = 'cmd_vel_backwards'

    # if forwardValue != -0.0:
    #     if forwardValue > 0:
    #         buttonResult = 'cmd_vel_forward'
    #     elif forwardValue < 0:
    #         buttonResult = 'cmd_vel_backwards'
    
    # Send button result to drone
    if not buttonResult == '':
        # Twist forward and backwards speed
        if buttonResult == 'cmd_vel_forward':
            sendTwist(0, 2, heightValue, 0, steeringValue, 0)
        elif buttonResult == 'cmd_vel_backwards':
            sendTwist(0, -2, heightValue, 0, steeringValue, 0)

        # Twist forward and backwards speed
        # if 'cmd_vel' in buttonResult:
        #     sendTwist(0, forwardValue, heightValue, 0, steeringValue, 0)
        
        # Default actions
        else:
            global buttonPub
            buttonPub = rospy.Publisher('/tello/' + buttonResult, Empty, queue_size=10)
            buttonPub.publish()


def steeringCase(data):
    # Global variables for speed
    global steeringValue
    global forwardValue

    # Initial input and button layout in accordence to joy topic
    inputs = []
    buttons = ["1", "2", "3", "4", "DOWN", "UP", "L2", "ST", "SE", "R2", "NULL", "L3", "R3", "HOME"]

    # Enumerate through sent data, if any of them are sent high (1), add them to the input list
    for idx, val in enumerate(data.buttons):
        if val == 1:
            inputs.append(buttons[idx])

    # Set steering and height values from joystick input
    steeringValue = _map(data.axes[0], -1, 1, 8, -8)
    # forwardValue = data.axes[3] * 2
    # print("DEBUG: FORWARDVALUE - " + str(forwardValue))
    return inputs


# Callback function used with joy subscriber
def callback(data):
    global joystickInputs
    # PS3 Controller
    joystickInputs = controllerCase(data)

    # Steering Wheel
    # joystickInputs = steeringCase(data)
    
    # If there are no buttons pressed, read from the analog joystick values and send a twist message that way
    if not 1 in data.buttons:
        sendTwist(leanValue, 0, heightValue, 0, 0, steeringValue)
    
    # Otherwise, iterate through the results, and then clear out the input list
    else:
        for inputResult in joystickInputs:
            # PS3 Controller
            parseInput(inputResult)

            # Steering Wheel
            # parseSteerInput(inputResult)
        joystickInputs[:] = []


# Standard ROS setup
def start():
    rospy.Subscriber("joy", Joy, callback)
    rospy.init_node('joyTello_node')
    rospy.spin()  


if __name__ == '__main__':
    start()