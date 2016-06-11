"""
If buttons are pressed on micro:bit, enter brightness menu loop
Displays current brightness, push buttons to go up and down
Waits 3 seconds, then saves current value to flash
How to influence neighboring values? Display brightness should monotonically increase with LDR value
If a user input is saved, any resulting non-monotonic parts of the curve can be "flattened"

Also, set a threshold for changing brightness. Check more frequently but only change it if LDR value changes by more than a threshold.
"""

from microbit import *

bright_lookup = dict()
for i in range(0, 1050, 50):
    bright_lookup[i] = i // 10


def round_down_50(x):
    # Round down to nearest multiple of 50; maps LDR values to brightness levels
    return x - (x % 50)


def push_button(pin_obj, count):
    # Cycles pin_num count number of times, to push corresponding buttons
    # Monitor doesn't recognize all presses if sleep values are decreased
    for i in range(count):
        pin_obj.write_digital(1)
        sleep(65)
        pin_obj.write_digital(0)
        sleep(65)

def change_brightness(increment):
    # Changes monitor brightness by increment steps, by pushing buttons
    # Push 'brightness up' button to enter brightness menu
    push_button(pin12, 1)
    sleep(500)
    # Going down
    if increment < 0:
        push_button(pin8, abs(increment))
    # Going up
    else:
        push_button(pin12, increment)
    sleep(200)  # Remove this to make things faster
    # Push 'menu' button to exit brightness menu
    push_button(pin16, 1)

def reset_to_0():
    # Resets brightness to 0 when program starts
    display.scroll("CALIBRATING", delay=80, wait=False)
    pin12.write_digital(1)
    sleep(100)
    pin12.write_digital(0)
    sleep(100)
    pin8.write_digital(1)
    sleep(6500)
    pin8.write_digital(0)
    sleep(100)
    pin16.write_digital(1)
    sleep(100)
    pin16.write_digital(0)
    sleep(500)

cur_bright = 0

# Main program execution
reset_to_0()

while True:
    ldr_val = pin0.read_analog()
    new_bright = bright_lookup[round_down_50(ldr_val)]
    # todo threshold so we aren't changing brightness all the time?
    if new_bright != cur_bright:
        display.scroll(str(new_bright), wait=False)
        change_brightness(new_bright - cur_bright)
        cur_bright = new_bright
    sleep(5000)
