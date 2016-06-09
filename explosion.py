from microbit import *

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

if __name__ == "__main__":
    show_explosion(2, 2)