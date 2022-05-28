import neopixel
import time
import board
import pyaudio
import audioop
import threading
import queue


def buildCols():
    cols = []

    # Define first column (left). Matrix is numbered zig-zag style left>right, right>left, left>right etc
    col = [0, 87, 88, 175, 176, 263, 264, 351, 352, 439, 440]
    cols.append(col)

    # Build remaining columns with a loop
    for x in range(1, num_cols):
        col = [col[0] + 1, col[1] - 1, col[2] + 1, col[3] - 1, col[4] + 1, col[5] - 1, col[6] + 1, col[7] - 1,
               col[8] + 1, col[9] - 1, col[10] + 1]
        cols.append(col)

    return cols

# Function not used in this instance
def buildRows():
    rows = []

    # Numbers in column 1 are odd/even/odd/even etc. This makes building the row arrays easy.
    for x in cols[0]:
        if (x % 2) == 0:
            row = [*range(x, x + num_cols)]
        else:
            row = [*range(x, x - num_cols, -1)]
        rows.append(row)

    return rows


def blankDisplay():
    pixels.fill((0, 0, 0))
    pixels.show()


def showFullBands(level):
    pixels.fill((0, 0, 0))
    # Take the list array and split into individual lists pertaining to each EQ band
    for eq in bands:
        # Now take the band list and split it into columns representing that band
        for bandCol in eq:
            # Then iterate over the pixels in each column which make up the band and turn them on
            for pix in bandCol[0:level]:
                pixels[pix] = (0, 255, 0)
    pixels.show()


def getBands(columns):
    # This needs tidying up!
    band1 = [columns[0], columns[1], columns[2], columns[3]]
    band2 = [columns[5], columns[6], columns[7], columns[8]]
    band3 = [columns[10], columns[11], columns[12], columns[13]]
    band4 = [columns[15], columns[16], columns[17], columns[18]]
    band5 = [columns[20], columns[21], columns[22], columns[23]]
    band6 = [columns[25], columns[26], columns[27], columns[28]]
    band7 = [columns[30], columns[31], columns[32], columns[33]]
    band8 = [columns[35], columns[36], columns[37], columns[38]]
    band9 = [columns[40], columns[41], columns[42], columns[43]]
    bands = [band1, band2, band3, band4, band5, band6, band7, band8, band9]
    return bands


def setRms():
    while True:
        stream.start_stream()
        data = stream.read(audioSlice)
        stream.stop_stream()
        rms = audioop.rms(data, 2)
        queue.append(rms)


##################################################

# Prepare board - this is a 11x44 NeoPixel panel (the posh one)
pixel_pin = board.D18
num_pixels = 484
num_cols = 44
num_rows = 11
# Have you seen it on full brightness? Have you seen it?!
ledBrightness = 0.2
# Send commands in batches
autoWrite = False
# Set pixel colour ordering
pixelOrder = neopixel.GRB
# Bring the panel up
pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=ledBrightness, auto_write=autoWrite, pixel_order=pixelOrder
)

# Build row/column lists
cols = buildCols()
rows = buildRows()
bands = getBands(cols)

# Give a visual indication flash that we're up and running
showFullBands(12)
time.sleep(0.5)
blankDisplay()

# Configure audio listener
# Audio source is an Alesis Core 1 wth OTG connection to Raspberry Pi Zero 2 W
audioSlice = 2048
audioRate = 48000
audioChannels = 1
maxValue = 2 ** 16
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=audioChannels, rate=audioRate, input=True,
                frames_per_buffer=audioSlice)
stream.stop_stream()
# Let PyAudio settle
time.sleep(1)

# Setup queue to push RMS values from listener thread, init var and fire listener thread
queue = []
crms = int()
audioMonitor = threading.Thread(target=setRms)
audioMonitor.start()

# Loop to evaluate RMS level by reading from thread queue
while True:
    if queue:
        crms = queue.pop(0)
        print(crms)
        if crms > 27000:
            showFullBands(12)
        elif crms > 25000:
            showFullBands(11)
        elif crms > 23000:
            showFullBands(10)
        elif crms > 21000:
            showFullBands(9)
        elif crms > 20000:
            showFullBands(8)
        elif crms > 19000:
            showFullBands(7)
        elif crms > 18000:
            showFullBands(6)
        elif crms > 17000:
            showFullBands(5)
        elif crms > 16000:
            showFullBands(4)
        elif crms > 15000:
            showFullBands(3)
        elif crms > 14000:
            showFullBands(2)
        elif crms > 13000:
            showFullBands(1)
        else:
            showFullBands(0)
