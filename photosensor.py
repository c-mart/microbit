from microbit import *

bright_lookup = dict()
for i in range(0, 1050, 50):
    bright_lookup[i] = i // 10


def round_down_50(x):
    # Round down to nearest multiple of 50; maps LDR values to brightness levels
    return x - (x % 50)

def push_button(pin_num, count):
    # Cycles pin_num count number of times, to push corresponding buttons
    pin_obj = eval("pin{0}".format(pin_num))
    for i in range(count):
        pin_obj.write_digital(1)
        sleep(50)
        pin_obj.write_digital(0)
        sleep(200)

def change_brightness(increment):
    # Changes monitor brightness by increment steps, by pushing buttons
    # Push 'brightness up' button to enter brightness menu
    push_button(12, 1)
    # Going down
    if increment < 0:
        push_button(8, abs(increment))
    # Going up
    else:
        push_button(12, increment)
    # Push 'menu' button to exit brightness menu
    push_button(16, 1)

cur_bright = 50

while True:
    ldr_val = pin0.read_analog()
    new_bright = bright_lookup[round_down_50(ldr_val)]
    # todo threshold so we aren't changing brightness all the time?
    if new_bright != cur_bright:
        display.scroll(str(new_bright), wait=False)
        change_brightness(new_bright - cur_bright)
        cur_bright = new_bright
    sleep(5000)
