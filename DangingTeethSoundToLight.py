import time
import board
import neopixel
import random
import pyaudio
import numpy as np
import audioop
import math

###########################################################################################################################

## START CONFIG SECTION ##

# GPIO control settings
pixel_pin =     board.D18
num_pixels =    256
order =         neopixel.GRB
brightness =    0.7

# LED panel config/init for GPIO. Using SPI actually makes it slower!!
pixels =        neopixel.NeoPixel(pixel_pin, num_pixels, brightness=brightness, auto_write=False, pixel_order=order)

# Define Teeth Resting State
tooth1 =        [ 0, 1, 14, 15, 17, 16 ]
tooth2 =        [ 32, 33, 34, 45, 46, 47, 50, 49, 48 ]
tooth3 =        [ 64, 65, 66, 67, 76, 77, 78, 79, 83, 82, 81, 80 ]
tooth4 =        [ 96, 97, 98, 99, 108, 109, 110, 111, 115, 114, 113, 112 ]   
tooth5 =        [ 128, 129, 130, 141, 142, 143, 146, 145, 144 ]
tooth6 =        [ 160, 161, 174, 177, 175, 176 ]
teeth =         [ tooth1, tooth2, tooth3, tooth4, tooth5, tooth6 ]

# Teeth Limits (Low/High Pixels)
tlow1 =         [ 1, 14, 17 ]
tlow2 =         [ 34, 45, 50 ]
tlow3 =         [ 67, 76, 83 ]
tlow4 =         [ 99, 108, 115 ]
tlow5 =         [ 130, 141, 146 ]
tlow6 =         [ 161, 174, 177 ] 
tlow =          [ tlow1, tlow2, tlow3, tlow4, tlow5, tlow6 ]

thigh1 =        [ 7, 8, 23 ]
thigh2 =        [ 39, 40, 55 ]
thigh3 =        [ 71, 72, 87 ]
thigh4 =        [ 103, 104, 119 ]
thigh5 =        [ 135, 136, 151 ]
thigh6 =        [ 167, 168, 183 ]
thigh =         [ thigh1, thigh2, thigh3, thigh4, thigh5, thigh6 ]

# Define RGB colours we are going to use
on =            [ 0, 255, 0 ]
off =           [ 0, 0, 0 ]
dim =           [ 0, 80, 0 ]
red =           [ 255, 0, 0 ]
yellow =        [ 255, 255, 0 ]
orange =        [ 230, 215, 0 ]

# Misc vars to prevent repeated teeth bouncess during randomisation
last =          0
index =         0

# Audio config settings - based on Alesis Core 1 input specs
chunk =         1024
freq =          48000
chans =         1

# EQ Bandings
eq1 =           (100, 100)
eq2 =           (200, 200)
eq3 =           (400, 400)
eq4 =           (800, 8000)
eq5 =           (1500, 1500)
eq6 =           (3000, 3000)
eq =            [ eq1, eq2, eq3, eq4, eq5, eq6 ] 

## END CONFIG SECTION ##

###########################################################################################################################

def freqanalyse(samples, sample_rate, *freqs):
    """
    Implementation of the Goertzel algorithm, useful for calculating individual
    terms of a discrete Fourier transform.

    `samples` is a windowed one-dimensional signal originally sampled at `sample_rate`.

    The function returns 2 arrays, one containing the actual frequencies calculated,
    the second the coefficients `(real part, imag part, power)` for each of those frequencies.
    For simple spectral analysis, the power is usually enough.

    Example of usage :
        
        freqs, results = goertzel(some_samples, 44100, (400, 500), (1000, 1100))
    """
    window_size = len(samples)
    f_step = sample_rate / float(window_size)
    f_step_normalized = 1.0 / window_size

    # Calculate all the DFT bins we have to compute to include frequencies
    # in `freqs`.
    bins = set()
    for f_range in freqs:
        f_start, f_end = f_range
        k_start = int(math.floor(f_start / f_step))
        k_end = int(math.ceil(f_end / f_step))

        if k_end > window_size - 1: raise ValueError('frequency out of range %s' % k_end)
        bins = bins.union(range(k_start, k_end))

    # For all the bins, calculate the DFT term
    n_range = range(0, window_size)
    freqs = []
    results = []
    for k in bins:

        # Bin frequency and coefficients for the computation
        f = k * f_step_normalized
        w_real = 2.0 * math.cos(2.0 * math.pi * f)
        w_imag = math.sin(2.0 * math.pi * f)

        # Doing the calculation on the whole sample
        d1, d2 = 0.0, 0.0
        for n in n_range:
            y  = samples[n] + w_real * d1 - d2
            d2, d1 = d1, y

        # Storing results `(real part, imag part, power)`
        results.append((
            0.5 * w_real * d1 - d2, w_imag * d1,
            d2**2 + d1**2 - w_real * d1 * d2)
        )
        freqs.append(int(round(f * sample_rate)))
    return freqs, results

# Blank pixels at startup
for x in range(0, num_pixels):
  pixels[x] = off
pixels.show()

# Draw teeth
for tooth in teeth:
  for x in tooth:
    pixels[x] = dim
pixels.show()

# Initialise PyAudio
maxValue = 2**16
p = pyaudio.PyAudio()

# Open the PyAudio and immediately stop it to prevent a buffer overrun
# Need to sleep for a second after init to let it settle 
stream = p.open(format=pyaudio.paInt16, channels=chans, rate=freq, input=True, frames_per_buffer=chunk)
stream.stop_stream()
time.sleep(1)

# Dance, Baby!
try:

  while True:

    # Get current amplitude
    stream.start_stream()
    data = stream.read(chunk)
    stream.stop_stream()
    rms = audioop.rms(data, 2)
    print("Amplitude: " + str(rms))
    
    # Static trigger amplitude for now 
    if rms > 10000:
      while index == last:
        index  = random.randint(0, 5)
      last = index

      # Get thresholds for selected tooth 
      state = tlow[index]
      low = tlow[index]
      high = thigh[index]
   
      # Add line for tooth 
      while state[0] < high[0]:
        if state[0] == high[0]-1 or state[0] == high[0]-2:
          pixels[state[0]+1] = red
          pixels[state[1]-1] = red
          pixels[state[2]+1] = red 
        elif state[0] == high[0]-3:
          pixels[state[0]+1] = orange
          pixels[state[1]-1] = orange
          pixels[state[2]+1] = orange
        elif state[0] == high[0]-4:
          pixels[state[0]+1] = yellow
          pixels[state[1]-1] = yellow
          pixels[state[2]+1] = yellow
        else:
          pixels[state[0]+1] = on
          pixels[state[1]-1] = on
          pixels[state[2]+1] = on
        pixels.show()
        state = [ state[0]+1, state[1]-1, state[2]+1 ]

      # Remove lowest line for tooth
      while state[0] > low[0]:
        pixels[state[0]] = off
        pixels[state[1]] = off
        pixels[state[2]] = off
        pixels.show()
        state = [ state[0]-1, state[1]+1, state[2]-1 ]

# Blank pixels when we CTRL-C out of the program and close/terminate the PyAudio stream
except KeyboardInterrupt:
  for x in range(0, num_pixels):
    pixels[x] = off
  pixels.show()
  stream.close()
  p.terminate()
