import sklib as tlib
import pygame
from time import sleep

# Initialize the GPIO server that provides live distance readings to other programs
# (optional: this is useful when running a separate display program).

# Initialize Pygame and joystick
pygame.init()
pygame.joystick.init()

joystick = pygame.joystick.Joystick(0)
joystick.init()
alert = False


# Axis mappings (may vary by controller)
AXIS_LSTICK_X = 0  # Left stick horizontal
AXIS_LT = 2       # Left trigger (stop)
AXIS_RT = 5       # Right trigger (accelerate)

# Some controllers map triggers as buttons (e.g., Xbox controllers).
BTN_LT = 6
BTN_RT = 7
BTN_X = 0  # Common Xbox A/X button index; adjust if needed for your controller

# How far the stick must move to count as “turning”
DEADZONE = 0.25

# Speed levels (controlled with D-Pad up/down)
SPEEDS = ['slow', 'mid', 'fast']
speed_index = 0

# Current motion state (prevents spamming the same command repeatedly)
_current_action = None  # "stop" | "forward" | "left" | "right"

# Get speed function by name
def move_forward_by_speed():
    if SPEEDS[speed_index] == 'slow':
        tlib.forward_slow()
    elif SPEEDS[speed_index] == 'mid':
        tlib.forward_mid()
    elif SPEEDS[speed_index] == 'fast':
        tlib.forward_fast()


def _set_action(action):
    """Set the current motion action, only applying it when it changes."""
    global _current_action
    if action == _current_action:
        #print(f"[DEBUG] action unchanged: {action}")
        return

    _current_action = action
    #print(f"[DEBUG] action changed to: {action}")

    if action == "stop":
        #print("[DEBUG] executing: stop")
        tlib.stop()
    elif action == "forward":
        #print("[DEBUG] executing: forward")
        move_forward_by_speed()
    elif action == "left":
        #print("[DEBUG] executing: left")
        tlib.direct_left()
    elif action == "right":
        #print("[DEBUG] executing: right")
        tlib.direct_right()


def _trigger_active(value):
    """Return True when a trigger is pressed.

    Many controllers report trigger rest as -1 and pressed as +1 (Xbox style).
    Some report rest as 0 and pressed as +1.
    """
    return value > 0.25


def handle_dpad(x, y):
    global speed_index

    if (x, y) == (0, 1):  # D-Pad Up
        speed_index = min(speed_index + 1, len(SPEEDS) - 1)
        print(f"[DEBUG] D-Pad up: speed set to {SPEEDS[speed_index]}")
        if _current_action == "forward":
            move_forward_by_speed()

    elif (x, y) == (0, -1):  # D-Pad Down
        speed_index = max(speed_index - 1, 0)
        print(f"[DEBUG] D-Pad down: speed set to {SPEEDS[speed_index]}")
        if _current_action == "forward":
            move_forward_by_speed()

try:
    print("Robot control started. Use left stick to turn, D-Pad to change speed, RT to accelerate, LT to stop.")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise KeyboardInterrupt
            elif event.type == pygame.JOYHATMOTION:
                x, y = event.value
                handle_dpad(x, y)
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == BTN_X:
                    print("[DEBUG] button X pressed: toggling LEDs")
                    tlib.toggle_leds(True)
                else:
                    print(f"[DEBUG] button {event.button} pressed")

        # Poll analog controls each loop (turning + triggers)
        x_axis = joystick.get_axis(AXIS_LSTICK_X) if joystick.get_numaxes() > AXIS_LSTICK_X else 0.0
        lt = joystick.get_axis(AXIS_LT) if joystick.get_numaxes() > AXIS_LT else 0.0
        rt = joystick.get_axis(AXIS_RT) if joystick.get_numaxes() > AXIS_RT else 0.0

        # Also allow triggers to be mapped as buttons (common on some gamepads)
        lt_button = joystick.get_button(BTN_LT) if joystick.get_numbuttons() > BTN_LT else False
        rt_button = joystick.get_button(BTN_RT) if joystick.get_numbuttons() > BTN_RT else False

        lt_active = _trigger_active(lt) or lt_button
        rt_active = _trigger_active(rt) or rt_button

        if lt_active:
            _set_action("stop")
        elif abs(x_axis) > DEADZONE:
            if x_axis < 0:
                _set_action("left")
            else:
                _set_action("right")
        elif rt_active:
            _set_action("forward")
        else:
            _set_action("stop")
        if tlib.distance_front() < 0.3:
            if alert == True:
                pass
            if alert == False:
                print("Obstacle détecté !")
                alert = True
        else:        
            if alert == True:
                print("Obstacle disparu.")
                alert = False
        
            
except KeyboardInterrupt:
    print("Exiting...")
finally:
    tlib.stop()
    pygame.quit()