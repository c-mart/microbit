"""
Wireless, multiplayer space shooter game for use with two micro:bits. Requires a firmware build with radio module.

Your spaceship is the pixel at the bottom of the screen, your opponent's spaceship is at the top of the screen.
Move your spaceship left or right by pressing the A or B button respectively.
To shoot a torpedo, press both buttons at the same time. After shooting you must wait a few seconds to reload.
Your spaceship will dim while reloading.

The game ends when a player is hit. Press the reset button to play again.
"""

from microbit import *
import radio

# Magic numbers
game_speed = 50  # Time step in milliseconds between game states. Lower numbers make the game run faster
reload_delay = 30  # Number of time steps that it takes to reload, during which you cannot shoot

# Initial setup
radio.on()
packet_header = b'qaivre'  # Prepended to all transmissions to avoid interference from other micro:bit radio activity
self_pos, other_pos = 2, 2
self_shoot, other_shoot = None, None  # None if not fired, otherwise tuple of x and y coordinates on display
self_cur_reload_delay, other_cur_reload_delay = 0, 0
self_score, other_score = 0, 0
game_over = False

def send_valid(packet):
    # Appends packet header to packet bytes object and transmits on the radio
    radio.send_bytes(packet_header + packet)


def recv_valid():
    # Checks for received radio transmission and validates it (confirms it starts with packet header)
    # Strips the packet header and returns message
    rec_raw = radio.receive_bytes()
    if rec_raw is not None and rec_raw.startswith(packet_header):
        return rec_raw[len(packet_header):]
    else:
        return None


def show_explosion(start_x, start_y):
    # Displays explosion growing outward from coordinate start_x, start_y
    display.set_pixel(start_x, start_y, 9)
    for blast_radius in range(8):
        for x in range(5):
            for y in range(5):
                if ((x - start_x)**2 + (y - start_y)**2)**0.5 <= blast_radius:
                    display.set_pixel(x, y, 9)
        blast_radius += 1
        sleep(50)
    for dim_val in range(8, 1, -1):
        for x in range(5):
            for y in range(5):
                display.set_pixel(x, y, dim_val)
        sleep(50)
    display.clear()


# Wait for other player to connect
connect_message_shown = False
while True:
    sleep(100)
    if recv_valid() == b'\xfe':
        send_valid(b'\xfe')
        display.scroll("GO", delay=80)
        break
    else:
        if connect_message_shown is False:
            display.scroll("CONNECTING", delay=80, wait=False)
            connect_message_shown = True
        send_valid(b'\xfe')


# Main loop of game
while True:
    # Restart game on game over
    if game_over:
        display.scroll(str(self_score) + ":" + str(other_score), delay=80, monospace=True)
        display.scroll("GO", delay=80)
        self_pos, other_pos = 2, 2
        self_shoot, other_shoot = None, None
        self_cur_reload_delay, other_cur_reload_delay = 0, 0
        game_over = False

    # Look for and act on button presses
    if button_a.is_pressed() and button_b.is_pressed():
        button_a.get_presses() and button_b.get_presses()  # Clear button presses
        if self_cur_reload_delay == 0: # Shoot the gun
            send_valid(b'\xff')
            self_shoot = (self_pos, 4)
            self_cur_reload_delay = reload_delay
    elif not(button_a.is_pressed()) and button_a.get_presses():  # Move left
        self_pos = max(self_pos - 1, 0)
        send_valid(bytes([self_pos]))
    elif not(button_b.is_pressed()) and button_b.get_presses():  # Move right
        self_pos = min(self_pos + 1, 4)
        send_valid(bytes([self_pos]))

    # Receive transmissions from the other player
    rec = recv_valid()
    if rec is not None:
        if 0 <= rec[0] <= 4:  # Other player moves
            other_pos = rec[0]
        elif rec == b'\xff':  # Other player shoots
            other_shoot = (4 - other_pos, 0)
            other_cur_reload_delay = reload_delay
        elif rec.startswith(b'\xfd'):  # Other player scores
            other_score = rec[1]

    # Draw spaceships
    display.clear()
    self_brightness = 5 if self_cur_reload_delay > 0 else 9
    other_brightness = 5 if other_cur_reload_delay > 0 else 9
    display.set_pixel(self_pos, 4, self_brightness)
    display.set_pixel(4 - other_pos, 0, other_brightness)

    # Handle shoot events, torpedo movement, and win conditions
    if self_shoot is not None:
        display.set_pixel(self_shoot[0], self_shoot[1], 9)  # Display the torpedo
        self_shoot = self_shoot[0], self_shoot[1] - 1  # Move the torpedo
        if self_shoot[1] < 0:
            if self_shoot[0] == 4 - other_pos:
                show_explosion(4 - other_pos, 0)
                self_score += 1
                game_over = True
                radio.send_bytes(b'\xfd' + bytes([self_score]))
            else:
                self_shoot = None
    if other_shoot is not None:
        display.set_pixel(other_shoot[0], other_shoot[1], 9)
        other_shoot = other_shoot[0], other_shoot[1] + 1
        if other_shoot[1] == 4:
            if other_shoot[0] == self_pos:
                show_explosion(self_pos, 4)
                other_score += 1
                game_over = True
            else:
                other_shoot = None

    # Decrement reload delays
    if self_cur_reload_delay > 0:
        self_cur_reload_delay -= 1
    if other_cur_reload_delay > 0:
        other_cur_reload_delay -= 1

    sleep(game_speed)
