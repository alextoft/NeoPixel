import time
import board
import neopixel
import random
import pyaudio
import audioop
import RPi.GPIO as GPIO
import logging

########################################################################################################################
## START CONFIG SECTION ##

# GPIO control settings
pixel_pin = board.D18  # GPIO pin - physical pin 12
num_pixels = 256
order = neopixel.GRB
brightness = 0.2

# Button config
mom_button_pin = 22  # Momentary switch GPIO pin designation - physical pin is 15 with physical pin 17 as 3.3v source
lat_button_pin = 4  # Latching switch GPIO designation - physical pin is 7 with physical pin 1 as 3.3v source
# Initialise the pins for the 2 available buttons
GPIO.setup(mom_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set initial value to LOW (off)
GPIO.setup(lat_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set initial value to LOW (off)
idleWait = 0.01  # 10ms to save on CPU cycles whilst PTT is disengaged
latchWait = 0.1  # 50ms to save on CPU cycles whilst looping waiting for display activation
# LED panel config/init for GPIO. Using SPI actually makes it slower!!
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=brightness, auto_write=False, pixel_order=order)

# Define Teeth Resting State
tooth1 = [0, 1, 14, 17, 16]
tooth2 = [31, 30, 29, 34, 45, 46, 47]
tooth3 = [48, 49, 50, 51, 60, 67, 66, 65, 64]
tooth4 = [79, 78, 77, 76, 75, 84, 92, 91, 93, 94, 95]
tooth5 = [96, 97, 98, 109, 114, 113, 112]
tooth6 = [127, 126, 129, 142, 143]
teeth = [tooth1, tooth2, tooth3, tooth4, tooth5, tooth6]

# Teeth Limits (Low/High Pixels)
tlow1 = [1, 14, 17]
tlow2 = [29, 34, 45]
tlow3 = [51, 60, 67]
tlow4 = [76, 83, 92]
tlow5 = [98, 109, 114]
tlow6 = [126, 129, 142]
tlow = [tlow1, tlow2, tlow3, tlow4, tlow5, tlow6]

thigh1 = [7, 8, 23]
thigh2 = [24, 39, 40]
thigh3 = [55, 56, 71]
thigh4 = [72, 87, 88]
thigh5 = [103, 114, 119]
thigh6 = [120, 135, 136]
thigh = [thigh1, thigh2, thigh3, thigh4, thigh5, thigh6]

blow1 = [1, 14, 17]
blow2 = [30, 33, 46]
blow3 = [49, 62, 65]
blow4 = [78, 81, 94]
blow5 = [97, 110, 113]
blow6 = [126, 129, 142]
blow = [blow1, blow2, blow3, blow4, blow5, blow6]

# Use tlow to bounce to normal teeth, or blow to allow teeth to equalise to 2px deep
lowtouse = blow

# Define RGB colours we are going to use
off = [0, 0, 0]
lg = [0, 255, 0]
dg = [0, 255, 20]
ly = [255, 255, 0]
dy = [204, 204, 20]
lr = [255, 0, 0]
dr = [255, 0, 20]

# Misc vars to prevent repeated teeth bouncesq during randomisation
last = 0
index = 0

# Audio config settings - based on Alesis Core 1 input specs
chunk = 1024
freq = 48000
chans = 1

thresh1 = 9000
thresh2 = 10000
thresh3 = 12000
thresh4 = 15000
thresh5 = 19000
thresh6 = 24000
thresh = [thresh1, thresh2, thresh3, thresh4, thresh5, thresh6]

# Multithread tooth sequences combinations
seq1 = "012345"
seq2 = "123450"
seq3 = "234501"
seq4 = "345012"
seq5 = "450123"
seq6 = "501234"
seq = [seq1, seq2, seq3, seq4, seq5, seq6]

# Version
lbversion = str("0.1")

# Sound to light setting
s2l = 0

# Require momentary button for S2L
s2lbut = 0


## END CONFIG SECTION ##
########################################################################################################################

########################################################################################################################
def bounce(index, brms):
    # logging.info("Bouncing tooth: " + str(index + 1))
    # Get thresholds
    low = lowtouse[index]
    high = thigh[index]
    state = low

    # Processing for D-U-D columns
    # Add line for tooth
    while (state[0] < high[0]) and (index == 0 or index == 2 or index == 4):
        if (state[0] == high[0] - 1) and (brms > thresh6):
            pixels[state[0] + 1] = lr
            pixels[state[1] - 1] = lr
            pixels[state[2] + 1] = lr
        elif state[0] == high[0] - 2 and (brms > thresh5):
            pixels[state[0] + 1] = ly
            pixels[state[1] - 1] = ly
            pixels[state[2] + 1] = ly
        elif state[0] == high[0] - 3 and (brms > thresh4):
            pixels[state[0] + 1] = lg
            pixels[state[1] - 1] = lg
            pixels[state[2] + 1] = lg
        elif state[0] == high[0] - 4 and (brms > thresh3):
            pixels[state[0] + 1] = lg
            pixels[state[1] - 1] = lg
            pixels[state[2] + 1] = lg
        elif state[0] == high[0] - 5 and (brms > thresh2):
            pixels[state[0] + 1] = lg
            pixels[state[1] - 1] = lg
            pixels[state[2] + 1] = lg
        elif state[0] == high[0] - 6 and (brms > thresh1):
            pixels[state[0] + 1] = lg
            pixels[state[1] - 1] = lg
            pixels[state[2] + 1] = lg
        # Remove Centre Pixel Above
        pixels[state[1]] = off
        # Write new pixel config to panel
        pixels.show()
        # Track the current row position state
        state = [state[0] + 1, state[1] - 1, state[2] + 1]

    # Remove lowest line for tooth
    while (state[0] > low[0]) and (index == 0 or index == 2 or index == 4):
        # Ascend Line
        pixels[state[0] - 1] = lg
        pixels[state[1] + 1] = lg
        pixels[state[2] - 1] = lg
        # Remove Line Below
        pixels[state[0]] = off
        pixels[state[1]] = off
        pixels[state[2]] = off
        pixels.show()
        state = [state[0] - 1, state[1] + 1, state[2] - 1]

    ##########################################################################################

    # Processing for U-D-U columns
    # Add line for tooth
    while (state[1] < high[1]) and (index == 1 or index == 3 or index == 5):
        if (state[1] == high[1] - 1) and (brms > thresh6):
            pixels[state[0] - 1] = dr
            pixels[state[1] + 1] = dr
            pixels[state[2] - 1] = dr
        elif state[1] == high[1] - 2 and (brms > thresh5):
            pixels[state[0] - 1] = dy
            pixels[state[1] + 1] = dy
            pixels[state[2] - 1] = dy
        elif state[1] == high[1] - 3 and (brms > thresh4):
            pixels[state[0] - 1] = dg
            pixels[state[1] + 1] = dg
            pixels[state[2] - 1] = dg
        elif state[1] == high[1] - 4 and (brms > thresh3):
            pixels[state[0] - 1] = dg
            pixels[state[1] + 1] = dg
            pixels[state[2] - 1] = dg
        elif state[1] == high[1] - 5 and (brms > thresh2):
            pixels[state[0] - 1] = dg
            pixels[state[1] + 1] = dg
            pixels[state[2] - 1] = dg
        elif state[1] == high[1] - 6 and (brms > thresh1):
            pixels[state[0] - 1] = dg
            pixels[state[1] + 1] = dg
            pixels[state[2] - 1] = dg
            # Remove Centre Pixel Above
        pixels[state[1] - 1] = off
        # Write new pixel config to panel
        pixels.show()
        # Track the current row position state
        state = [state[0] - 1, state[1] + 1, state[2] - 1]

    # Remove lowest line for tooth
    while (state[1] > low[1]) and (index == 1 or index == 3 or index == 5):
        # Ascend Line
        pixels[state[0] + 1] = dg
        pixels[state[1] - 1] = dg
        pixels[state[2] + 1] = dg
        # Remove Line Below
        pixels[state[0]] = off
        pixels[state[1]] = off
        pixels[state[2]] = off
        # Write new pixel config to panel
        pixels.show()
        # Track the current row position state
        state = [state[0] + 1, state[1] - 1, state[2] + 1]


## End of bounce function ##
########################################################################################################################

########################################################################################################################
## Start of getRms function ##
def getRms():
    if s2l == 1:
        stream.start_stream()
        data = stream.read(chunk)
        stream.stop_stream()
        rms = audioop.rms(data, 2)
        logging.debug("Amplitude: " + str(rms))
        return rms
    else:
        return int(random.choice(thresh) + 1)


## End of getRms function ##
########################################################################################################################

########################################################################################################################
## Start of blankPixels function ##
def blankPixels():
    for x in range(0, num_pixels):
        pixels[x] = off
    pixels.show()


## End of blankPixels function ##
########################################################################################################################

########################################################################################################################
## Start of blankPixels function ##
def resetTeeth():
    col = lg
    for tooth in teeth:
        for x in tooth:
            pixels[x] = col
        if col == lg:
            col = dg
        else:
            col = lg
    pixels.show()


## End of blankPixels function ##
########################################################################################################################
## Start prep ##

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info("LoopBot v" + lbversion + " starting up")

if s2l == 1:
    # Initialise PyAudio, start/stop stream to prevent buffer overrun and sleep to settle during init
    logging.info("Initialising audio listener, ignore Jack Server errors...")
    logging.info("No try/except has been used, hence Python will crash if audio input cannot be detected")
    maxValue = 2 ** 16
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=chans, rate=freq, input=True, frames_per_buffer=chunk)
    stream.stop_stream()
    time.sleep(1)
    logging.info("Audio init complete")
else:
    logging.info("Sound trigger disabled in config")

if GPIO.input(lat_button_pin) == GPIO.LOW:
    logging.info("Latch switch disengaged - toggle to start")
while GPIO.input(lat_button_pin) == GPIO.LOW:
    time.sleep(latchWait)
logging.info("Latch switch engaged - drawing resting teeth - hold momentary switch to bounce")
blankPixels()
resetTeeth()

## End prep ##
########################################################################################################################

########################################################################################################################
# Main loop ##

try:
    momButtonDown = 0
    displayOff = 0
    while True:
        if (GPIO.input(mom_button_pin) == GPIO.HIGH and GPIO.input(lat_button_pin) == GPIO.HIGH) or (
                s2lbut == 1 and s2l == 0):
            if momButtonDown == 0:
                logging.info("Momentary switch held (or disabled) - bouncing teeth")
            momButtonDown = 1
            rms = getRms()
            if rms > thresh1:
                while index == last:
                    index = random.randint(0, 5)
                last = index
                bounce(index, rms)
        elif (GPIO.input(mom_button_pin) == GPIO.LOW and GPIO.input(
                lat_button_pin) == GPIO.HIGH and momButtonDown == 1) or (s2lbut == 1 and s2l == 1):
            logging.info("Momentary switch released - resetting display to resting teeth")
            logging.info("Hold momentary switch to bounce or toggle latch switch to blank display")
            blankPixels()
            resetTeeth()
            momButtonDown = 0  # This stops constant re-drawing of the teeth whilst the momentary switch is LOW
            time.sleep(idleWait)
        elif GPIO.input(lat_button_pin) == GPIO.LOW:
            logging.info("Latch switch disengaged - blanking display")
            blankPixels()
            displayOff = 1
            while GPIO.input(lat_button_pin) == GPIO.LOW:
                time.sleep(latchWait)
        elif GPIO.input(lat_button_pin) == GPIO.HIGH and displayOff == 1:
            logging.info("Latch switch engaged - activating display")
            displayOff = 0
            resetTeeth()


# Blank pixels when we CTRL-C out of the program and close/terminate the PyAudio stream
except KeyboardInterrupt:
    for x in range(0, num_pixels):
        pixels[x] = off
    pixels.show()
    print("\n")
    if s2l == 1:
        stream.close()
        p.terminate()
        logging.info("Shutting down audio stream")
    logging.critical("Process forcibly terminated - killed by death!")

## End main loop ##
########################################################################################################################
