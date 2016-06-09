from microbit import *

bright_lookup = dict()
for i in range(0, 1050, 50):
    bright_lookup[i] = i // 10


def round_down_50(x):
    # Round down to nearest multiple of 50; maps LDR values to brightness levels
    return x - (x % 50)

def change_brightness(val_from, val_to):
    #

while True:
    ldr_val = pin0.read_analog()
    bright = bright_lookup[round_down_50(ldr_val)]
    display.scroll(str(bright))
    sleep(5000)