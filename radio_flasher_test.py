from microbit import *
import radio

radio.enable(32, 4)

was_pressed = False
while True:
    is_pressed = button_a.is_pressed()
    if is_pressed is not was_pressed:
        if is_pressed is True:
            radio.send(b'\x01')
        else:
            radio.send(b'\x00')
    was_pressed = is_pressed
    rec = radio.recv()
    if rec == b'\x01':
        display.show(Image("99999:99999:99999:99999:99999"))
    elif rec == b'\x00':
        display.clear()
    sleep(5)