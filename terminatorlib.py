"""Library for the Terminator Robot.

This module exposes motor-control helpers and a simple distance IPC server.

The hardware (GPIO) objects are lazily initialized, so importing this module alone
does not open GPIO pins. Call `init_motors()` and/or `init_sonar()` as needed.
"""

import threading
import socket
import socketserver
import time
from gpiozero import PWMOutputDevice, DistanceSensor
from time import sleep

# Hardware objects (lazily initialized)
motor_left_forward = None
motor_left_backward = None
motor_right_forward = None
motor_right_backward = None
motor_backleft_forward = None
motor_backleft_backward = None
motor_backright_forward = None
motor_backright_backward = None
sonar = None
led12 = None
led34 = None
led56 = None

# --- Initialization helpers --------------------------------------------------

def _init_motors():
    """Initialize GPIO objects for the motors (idempotent)."""
    global motor_left_forward, motor_left_backward, motor_right_forward, motor_right_backward
    global motor_backleft_forward, motor_backleft_backward, motor_backright_forward, motor_backright_backward

    if motor_left_forward is not None:
        return

    motor_left_forward = PWMOutputDevice(17)
    motor_left_backward = PWMOutputDevice(27)
    motor_right_forward = PWMOutputDevice(3)
    motor_right_backward = PWMOutputDevice(2)
    motor_backleft_forward = PWMOutputDevice(10)
    motor_backleft_backward = PWMOutputDevice(9)
    motor_backright_forward = PWMOutputDevice(19)
    motor_backright_backward = PWMOutputDevice(26)


def _init_sonar():
    """Initialize the ultrasonic sensor (idempotent)."""
    global sonar
    if sonar is not None:
        return
    sonar = DistanceSensor(echo=4, trigger=22, max_distance=1.0)


def init_motors():
    """Public helper to initialize motors.

    Call this from the control program before using any movement helpers.
    """
    _init_motors()


def init_sonar():
    """Public helper to initialize the distance sensor."""
    _init_sonar()

def init_leds():
    """Public helper to initialize the LEDs."""
    global led12, led34, led56
    if led12 is not None:
        return
    led12 = PWMOutputDevice(16)
    led34 = PWMOutputDevice(20)
    led56 = PWMOutputDevice(21)


# --- Motor control helpers ---------------------------------------------------

def forward_slow():
    """Move the robot forward slowly (0.4)."""
    _init_motors()
    motor_left_forward.value = 0.4  # Set the motor to move forward at half speed
    motor_left_backward.value = 0  # Stop the backward motor
    motor_right_forward.value = 0.4  # Set the motor to move forward at half speed
    motor_right_backward.value = 0  # Stop the backward motor
    motor_backleft_forward.value = 0.4  # Set the motor to move forward at half speed
    motor_backleft_backward.value = 0  # Stop the backward motor
    motor_backright_forward.value = 0.4  # Set the motor to move forward at half speed
    motor_backright_backward.value = 0  # Stop the backward motor


def forward_mid():
    """Move the robot forward at medium speed (0.7)."""
    _init_motors()
    motor_left_forward.value = 0.7  # Set the motor to move forward at medium speed
    motor_left_backward.value = 0  # Stop the backward motor
    motor_right_forward.value = 0.7  # Set the motor to move forward at medium speed
    motor_right_backward.value = 0  # Stop the backward motor
    motor_backleft_forward.value = 0.7  # Set the motor to move forward at medium speed
    motor_backleft_backward.value = 0  # Stop the backward motor
    motor_backright_forward.value = 0.7  # Set the motor to move forward at medium speed
    motor_backright_backward.value = 0  # Stop the backward motor


def forward_fast():
    """Move the robot forward at full speed (1)."""
    _init_motors()
    motor_left_forward.value = 1.0  # Set the motor to move forward at full speed
    motor_left_backward.value = 0  # Stop the backward motor
    motor_right_forward.value = 1.0  # Set the motor to move forward at full speed
    motor_right_backward.value = 0  # Stop the backward motor
    motor_backleft_forward.value = 1.0  # Set the motor to move forward at full speed
    motor_backleft_backward.value = 0  # Stop the backward motor
    motor_backright_forward.value = 1.0  # Set the motor to move forward at full speed
    motor_backright_backward.value = 0  # Stop the backward motor


def backward_slow():
    """Move the robot backward slowly (0.4)."""
    _init_motors()
    motor_left_backward.value = 0.4  # Set the motor to move backward at half speed
    motor_left_forward.value = 0  # Stop the forward motor
    motor_right_backward.value = 0.4  # Set the motor to move backward at half speed
    motor_right_forward.value = 0  # Stop the forward motor
    motor_backleft_backward.value = 0.4  # Set the motor to move backward at half speed
    motor_backleft_forward.value = 0  # Stop the forward motor
    motor_backright_backward.value = 0.4  # Set the motor to move backward at half speed
    motor_backright_forward.value = 0  # Stop the forward motor


def backward_fast():
    """Move the robot backward at full speed (0.7)."""
    _init_motors()
    motor_left_backward.value = 0.7  # Set the motor to move backward at full speed
    motor_left_forward.value = 0  # Stop the forward motor
    motor_right_backward.value = 0.7  # Set the motor to move backward at full speed
    motor_right_forward.value = 0  # Stop the forward motor
    motor_backleft_backward.value = 0.7  # Set the motor to move backward at full speed
    motor_backleft_forward.value = 0  # Stop the forward motor
    motor_backright_backward.value = 0.7  # Set the motor to move backward at full speed
    motor_backright_forward.value = 0  # Stop the forward motor


def stop():
    """Stop the robot."""
    _init_motors()
    motor_left_forward.value = 0  # Stop the forward motor
    motor_left_backward.value = 0  # Stop the backward motor
    motor_right_forward.value = 0  # Stop the forward motor
    motor_right_backward.value = 0  # Stop the backward motor
    motor_backleft_forward.value = 0  # Stop the forward motor
    motor_backleft_backward.value = 0  # Stop the backward motor
    motor_backright_forward.value = 0  # Stop the forward motor
    motor_backright_backward.value = 0  # Stop the backward motor


def direct_left():
    """Rotate the robot to the left (F-B)."""
    _init_motors()
    motor_left_forward.value = 0  # Stop the forward motor
    motor_left_backward.value = 0.4  # Set the motor to move backward at half speed
    motor_right_forward.value = 0.4  # Set the motor to move forward at half speed
    motor_right_backward.value = 0  # Stop the backward motor
    motor_backleft_forward.value = 0  # Stop the forward motor
    motor_backleft_backward.value = 0.4  # Set the motor to move backward at half speed
    motor_backright_forward.value = 0.4  # Set the motor to move forward at half speed
    motor_backright_backward.value = 0  # Stop the backward motor


def direct_right():
    """Rotate the robot to the right (B-F)."""
    _init_motors()
    motor_left_forward.value = 0.4  # Set the motor to move forward at half speed
    motor_left_backward.value = 0  # Stop the backward motor
    motor_right_forward.value = 0  # Stop the forward motor
    motor_right_backward.value = 0.4  # Set the motor to move backward at half speed
    motor_backleft_forward.value = 0.4  # Set the motor to move forward at half speed
    motor_backleft_backward.value = 0  # Stop the backward motor
    motor_backright_forward.value = 0  # Stop the forward motor
    motor_backright_backward.value = 0.4  # Set the motor to move backward at half speed


def turn_left():
    """Rotate the robot to the left (0.6-0.4) (This needs more testing)."""
    _init_motors()
    motor_left_forward.value = 0.6  # Set the motor to move forward at half speed
    motor_left_backward.value = 0  # Stop the backward motor
    motor_right_forward.value = 0.4  # Set the motor to move forward at half speed
    motor_right_backward.value = 0  # Stop the backward motor
    motor_backleft_forward.value = 0.6  # Set the motor to move forward at half speed
    motor_backleft_backward.value = 0  # Stop the backward motor
    motor_backright_forward.value = 0.4  # Set the motor to move forward at half speed
    motor_backright_backward.value = 0  # Stop the backward motor


def turn_right():
    """Rotate the robot to the right (0.4-0.6) (This needs more testing)."""
    _init_motors()
    motor_left_forward.value = 0.4  # Set the motor to move forward at half speed
    motor_left_backward.value = 0  # Stop the backward motor
    motor_right_forward.value = 0.6  # Set the motor to move forward at half speed
    motor_right_backward.value = 0  # Stop the backward motor
    motor_backleft_forward.value = 0.4  # Set the motor to move forward at half speed
    motor_backleft_backward.value = 0  # Stop the backward motor
    motor_backright_forward.value = 0.6  # Set the motor to move forward at half speed
    motor_backright_backward.value = 0  # Stop the backward motor


def distance_front():
    """Get the distance from the ultrasonic sensor."""
    _init_sonar()
    return sonar.distance  # Return the distance from the ultrasonic sensor

def toggle_leds(state):
    """Toggle the LEDs on or off."""
    init_leds()
    led12.toggle()  # Toggle LED 1 and 2
    led34.toggle()  # Toggle LED 3 and 4
    led56.toggle()  # Toggle LED 5 and 6


