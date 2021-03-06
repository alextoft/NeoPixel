import neopixel
import time
import board
import random

def buildCols():
  cols = [] 
  
  # Define first column (left). Matrix is numbered zig-zag style left>right, right>left, left>right etc 
  col = [0, 87, 88, 175, 176, 263, 264, 351, 352, 439, 440]
  cols.append(col)

  # Build remaining columns with a loop
  for x in range(1, num_cols):
    col = [col[0]+1, col[1]-1, col[2]+1, col[3]-1, col[4]+1, col[5]-1, col[6]+1, col[7]-1, col[8]+1, col[9]-1, col[10]+1]
    cols.append(col)
  
  return cols

def buildRows():
  rows = []
  
  # Numbers in column 1 are odd/even/odd/even etc. This makes building the row arrays easy.
  for x in cols[0]:
    if(x % 2) == 0:
      row = [*range(x, x+num_cols)]
    else:
      row = [*range(x, x-num_cols, -1)] 
    rows.append(row)
 
  return rows 

def blankDisplay():
  pixels.fill((0,0,0))
  pixels.show()

def sweep(data):
  sCol = getColour()  
  for items in data:
    for x in items:
      pixels[x] = (sCol[0], sCol[1], sCol[2])
    pixels.show()
  blankDisplay()

def reverseSweep(data):
  sCol = getColour()
  for items in reversed(data):
    for x in items:
      pixels[x] = (sCol[0], sCol[1], sCol[2]) 
    pixels.show()
  blankDisplay()

def fourWaySweep():
  sweep(cols)
  sweep(rows)
  reverseSweep(cols)
  reverseSweep(rows)

def getColour():
  colours = [[255,0,0], [0,255,0], [0,0,255], [255,255,0], [0,255,255], [255,0,255], [192,192,192], [128,0,0], [128,128,0], [0,128,0], [128,0,128], [0,128,128], [0,0,128]]
  return random.choice(colours)

##################################################

# Prepare board
pixel_pin = board.D18
num_pixels = 484
num_cols = 44
num_rows = 11
ledBrightness = 0.2
autoWrite = False
pixelOrder = neopixel.GRB
pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=ledBrightness, auto_write=autoWrite, pixel_order=pixelOrder
)

# Build row/column lists
cols = buildCols()
rows = buildRows()

# Do stuff
while True:
  fourWaySweep()
