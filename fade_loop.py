from microbit import *

def find_brightest_pixel(image):
    # Return brightness of brightest pixel in image
    brightest = None
    for char in repr(image):
        if char in "0123456789":
            if brightest is None or int(char) > brightest:
                brightest = int(char)
    return brightest

def fade_loop_anim(orig_image):
    # Create a fade animation (to dark and bright again)
    anim = list()
    anim_len = find_brightest_pixel(orig_image)
    for i in range(anim_len + 1):
        next_image_array = [[None for _ in range(5)] for _ in range(5)]
        for x in range(5):
            for y in range(5):
                new_pixel = orig_image.get_pixel(x, y) - i
                next_image_array[y][x] = str(max(new_pixel, 0))
        next_image = Image(":".join(["".join([char for char in row]) for row in next_image_array]))
        anim.append(next_image)
    anim = anim + anim[::-1] + 5 * [orig_image]
    return anim

if __name__ == "__main__":
    play_pause = Image("90900:90990:90999:90990:90900")
    pp_fade_loop_anim = fade_loop_anim(play_pause)
    display.show(pp_fade_loop_anim, loop=True, delay=50)