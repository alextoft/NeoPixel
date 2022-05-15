import board
import neopixel

pixel_pin = board.D18 
num_pixels = 144
order = neopixel.GRB
brightness = 1

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=brightness, auto_write=True, pixel_order=order)

stripes = [ 0, 3, 13, 17, 31, 6, 10, 20, 28, 34, 46, 48, 23, 25, 37, 43, 51, 61, 65, 79, 40, 54, 58, 68, 76, 82, 94, 96, 71, 73, 85, 91, 99, 109, 113, 127, 88, 102, 106, 116, 124, 130, 142, 119, 121, 133, 139, 136 ]

colours = [ [ 255, 0, 0 ], [ 0, 255, 0 ], [ 0, 0, 255] ]

for col in colours:
    for x in stripes:
        pixels[x] = col
    for x in stripes:
        pixels[x] = [ 0, 0, 0 ]

quit()
