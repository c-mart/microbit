"""
Author: Chris Martin

Automatically controls brightness of ASUS VN248 LCD monitor using ambient light level measured by a photosensor.
Responds to user adjustment via buttons; updates internal brightness map to remember user preferences.
Requires connection to photosensor, and wiring harness to monitor button control panel.

GPIO pin usage
Pin 0: read value from photoresistor (LDR)
Pin 2: read voltage applied to monitor power LED to determine on/off state
Pin 8: send 'brightness down' command
Pin 12: send 'brightness up' and 'enter brightness menu' commands
Pin 16: send 'exit brightness menu' command

TODO:
- Calculate relative change instead of flattening when changing bright_map? Perhaps a better algorithm exists
- Save bright_map to flash memory to remember between reboots

TADA:
- Don't do anything if monitor is off, detect this with voltage on LED pin?
- If buttons are pressed on micro:bit, enter brightness menu loop. Displays current brightness, push buttons to go up and down. Waits 3 seconds, then saves current value to flash
- How to influence neighboring values? Display brightness should monotonically increase with LDR value. If a user input is saved, any resulting non-monotonic parts of the curve can be "flattened"
- Also, set a threshold for changing brightness. Check more frequently but only change it if LDR value changes by more than a threshold.
- Each press of a button should change brightness for watching feedback
"""

from microbit import *

# Ensure no voltage on pin used for sensing monitor power state
pin2.write_digital(0)

# Build initial brightness map
bright_map = dict()
for i in range(0, 1050, 50):
    bright_map[i] = i // 10


def round_down_50(x):
    # Round down to nearest multiple of 50; maps LDR values to brightness levels
    return x - (x % 50)


def press_button(pin_obj, count=1, press_duration=65):
    # Cycles pin_num count number of times, to press corresponding buttons for press_duration milliseconds
    # Monitor doesn't recognize all presses if press_duration/sleep values are decreased from default
    for i in range(count):
        pin_obj.write_digital(1)
        sleep(press_duration)
        pin_obj.write_digital(0)
        sleep(65)


def change_brightness(increment, enter_exit_menu=True):
    # Changes monitor brightness by increment steps; negative increment will decrease brightness
    if enter_exit_menu:
        # Push 'brightness up' button to enter brightness menu
        press_button(pin12)
        sleep(500)
    # Going down
    if increment < 0:
        press_button(pin8, abs(increment))
    # Going up
    else:
        press_button(pin12, increment)
    if enter_exit_menu:
        sleep(200)
        # Push 'menu' button to exit brightness menu
        press_button(pin16)


def reset_to_0():
    # Resets brightness to 0 when program starts
    display.scroll("INITIALIZING", delay=80, wait=False)
    press_button(pin12)  # Enter brightness menu
    sleep(100)
    press_button(pin8, press_duration=6500)  # Hold down button to bring brightness to 0
    sleep(50)
    press_button(pin16)  # Exit brightness menu
    sleep(400)


def get_presses():
    # Get presses of both buttons, returns tuple
    return button_a.get_presses(), button_b.get_presses()


def update_bright_map(ldr_val, new_bright):
    # Update brightness map based on user input
    bright_map[round_down_50(ldr_val)] = new_bright
    # Iterate through map and adjust so it is monotonically increasing
    for possible_ldr_val in range(0, 1050, 50):
        if (possible_ldr_val > ldr_val and bright_map[possible_ldr_val] < new_bright) or \
           (possible_ldr_val < ldr_val and bright_map[possible_ldr_val] > new_bright):
            bright_map[possible_ldr_val] = new_bright


def user_adjust(cur_bright, ldr_val):
    # Accept adjustment from user, update map and set new brightness
    display.scroll(str(cur_bright), delay=80, wait=False)
    new_bright = cur_bright

    # Push 'brightness up' button to enter brightness menu
    press_button(pin12)
    sleep(500)

    # Loop handles button presses, times out after 3 seconds
    last_input_time = running_time()
    while True:
        a_presses, b_presses = get_presses()
        if (a_presses and new_bright > 0) or (b_presses and new_bright < 100):
            change = (-5 * a_presses) + (5 * b_presses)
            new_bright += change
            display.scroll(str(new_bright), delay=80, wait=False)
            change_brightness(change, enter_exit_menu=False)
            last_input_time = running_time()
        elif running_time() > (last_input_time + 3000):
            break
        sleep(50)

    # Exit brightness menu
    press_button(pin16)
    # If user adjusted brightness, return new value
    if new_bright != cur_bright:
        update_bright_map(ldr_val, new_bright)
    return new_bright


# Main program execution
mon_pwr_state = False
while True:

    # Tests monitor power state, only exists when monitor is on and set to known brightness level
    while True:
        if mon_pwr_state is True:
            if pin2.read_analog() > 700:
                break  # Monitor is still on
            else:
                mon_pwr_state = False  # Go to sleep
        elif mon_pwr_state is False:
            if pin2.read_analog() > 700:
                mon_pwr_state = True  # Waking up
                # Wait a few seconds for monitor to fully power on, then initialize
                sleep(11000)
                reset_to_0()
                cur_bright = 0
                # LDR value stored w/ each brightness change to threshold future changes
                last_change_ldr_val = None
                get_presses()  # Clear any button presses accumulated during sleep
                break
            else:
                sleep(1000)  # Monitor still asleep, check again in a second

    cur_ldr_val = pin0.read_analog()
    a_presses, b_presses = get_presses()
    if a_presses or b_presses:
        new_bright = user_adjust(cur_bright, cur_ldr_val)
    elif last_change_ldr_val is None or abs(cur_ldr_val - last_change_ldr_val) >= 50:
        new_bright = bright_map[round_down_50(cur_ldr_val)]
        display.scroll(str(new_bright), wait=False)
        change_brightness(new_bright - cur_bright)
        sleep(1500)

    if new_bright != cur_bright:
        cur_bright = new_bright
        last_change_ldr_val = cur_ldr_val
    sleep(500)