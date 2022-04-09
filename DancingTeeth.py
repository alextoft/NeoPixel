import time
import board
import neopixel
import random

# GPIO control settings
pixel_pin = board.D18
num_pixels = 256
order = neopixel.GRB

# Individual pixel characteristics
pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.9, auto_write=False, pixel_order=order
)

# Define Teeth Resting State
tooth1 = [ 0, 1, 14, 17, 16 ]
tooth2 = [ 32, 33, 34, 45, 50, 49, 48 ]
tooth3 = [ 64, 65, 66, 67, 76, 83, 82, 81, 80 ]
tooth4 = [ 96, 97, 98, 99, 108, 115, 114, 113, 112 ]   
tooth5 = [ 128, 129, 130, 141, 146, 145, 144 ]
tooth6 = [ 160, 161, 174, 177, 176 ]
teeth = [ tooth1, tooth2, tooth3, tooth4, tooth5, tooth6 ]

# Teeth Limits (Low/High Pixels)
tlow1 = [ 1, 14, 17 ]
tlow2 = [ 34, 45, 50 ]
tlow3 = [ 67, 76, 83 ]
tlow4 = [ 99, 108, 115 ]
tlow5 = [ 130, 141, 146 ]
tlow6 = [ 161, 174, 177 ] 
tlow = [ tlow1, tlow2, tlow3, tlow4, tlow5, tlow6 ]

thigh1 = [ 7, 8, 23 ]
thigh2 = [ 39, 40, 55 ]
thigh3 = [ 71, 72, 87 ]
thigh4 = [ 103, 104, 119 ]
thigh5 = [ 135, 136, 151 ]
thigh6 = [ 167, 168, 183 ]
thigh = [ thigh1, thigh2, thigh3, thigh4, thigh5, thigh6 ]

# Define RGB colours we are going to use
on = [ 0, 255, 0 ]
off = [ 0, 0, 0 ]

# Reset Pixels & Pause
for x in range(0,255):
  pixels[x] = off
pixels.show()
time.sleep(3)

# Draw Teeth & Pause
for tooth in teeth:
  for x in tooth:
    pixels[x] = on
pixels.show()
time.sleep(3)

# Dance, Baby!
while True:
  for x in teeth:
    index = random.randint(0, 5)
    state = tlow[index]
    low = tlow[index]
    high = thigh[index]
    while state[0] < high[0]:
      # Descend Line
      pixels[state[0]+1] = on
      pixels[state[1]-1] = on
      pixels[state[2]+1] = on
      # Remove Centre Pixel Above
      pixels[state[1]] = off
      pixels.show()
      state = [ state[0]+1, state[1]-1, state[2]+1 ]
    while state[0] > low[0]:
      # Ascend Line
      pixels[state[0]-1] = on
      pixels[state[1]+1] = on
      pixels[state[2]-1] = on
      # Remove Line Below
      pixels[state[0]] = off
      pixels[state[1]] = off
      pixels[state[2]] = off
      pixels.show()
      state = [ state[0]-1, state[1]+1, state[2]-1 ]

