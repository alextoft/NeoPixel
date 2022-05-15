import os
import sys
import time
import board
import neopixel
import evdev
import threading
from datetime import datetime

pixel_pin = board.D18
num_pixels = 144
# This is the host machine MAC - it will need customising
btMac = "b8:27:eb:60:5c:77"

global go

try:
    ORDER = neopixel.GRB

    pixels = neopixel.NeoPixel(
        pixel_pin, num_pixels, brightness=0.1, auto_write=False, pixel_order=ORDER
    )

    def trackButton():
        doOutput("BLE button tracker thread running")
        global go
        while True:
            try:
                doOutput("Monitoring for button activity")
                for event in device.read_loop():
                    if event.type == evdev.ecodes.EV_KEY:
                        data = evdev.categorize(event)
                        if event.code == 330 and data.keystate == 0 and go == 0:
                            doOutput("Short Push - LED panel Rainbow ON")
                            go = 1
                        elif event.code == 330 and data.keystate == 0 and go == 1:
                            doOutput("Short Push - LED panel Rainbow OFF")
                            go = 0
                        elif event.code == 114 and data.keystate == 0:
                            doOutput("Long push - Rebooting!")
                            os.system('/usr/sbin/reboot') 
            except:
                doOutput("Bluetooth is having an issue. Glitch or timeout? Who knows. Restarting program.")
                sys.stdout.flush()
                os.execv(sys.executable, ['python'] + [sys.argv[0]])

    def panel(pos):
        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r = int(pos * 3)
            g = int(255 - pos * 3)
            b = 0
        elif pos < 170:
            pos -= 85
            r = int(255 - pos * 3)
            g = 0
            b = int(pos * 3)
        else:
            pos -= 170
            r = 0
            g = int(pos * 3)
            b = int(255 - pos * 3)
        return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)

    def rainbow():
        for j in range(255):
            for i in range(num_pixels):
                pixel_index = (i * 256 // num_pixels) + j
                pixels[i] = panel(pixel_index & 255)
                if go == 0:
                    blankDisplay()
                    break
            pixels.show()

    def doOutput(msg):
        now = datetime.now()
        print(now.strftime("%Y-%m-%d %H:%M:%S") + " " + msg)

    def blankDisplay():
        pixels.fill((0,0,0))
        pixels.show()

#######

    doOutput("Modified rainbow LED demo with BLE button control v0.0001")
    blankDisplay()
    buttonPresent = 0
    butMsg = 0
    blueLed = 0
    while buttonPresent == 0:
        try:
            while buttonPresent == 0:
                # This is a disgrace. Device needs enumerating properly.
                device = evdev.InputDevice('/dev/input/event2')
                if str(device.phys) == btMac:
                    doOutput("BLE button detected. Let's go!")
                    buttonPresent = 1 
                    pixels[0] = [ 0, 255, 0 ]
                    pixels.show()
                    time.sleep(0.1)
                    blueLed = 1
        except:
            if butMsg == 0:
                doOutput("Waiting for button device to appear (click it!)") 
                butMsg = 1
            # Blink top left pixel while waiting for BLE device to appear
            if blueLed == 0:
                pixels[0] = [0, 0, 255]
                pixels.show()
                blueLed = 1
            elif blueLed == 1:
                pixels[0] = [0, 0, 0]
                pixels.show()
                blueLed = 0
            time.sleep(0.2)

    blankDisplay()
    buttonMonitor = threading.Thread(target=trackButton)
    buttonMonitor.start()
    go = 0 
    while True:
        while go == 1:
            rainbow()
        time.sleep(0.01)

except KeyboardInterrupt:
    blankDisplay()
    doOutput("Killed by death!")
    quit()
