import RPi.GPIO as gpio
import time

gpio.setmode(gpio.BCM)
gpio.setup(20, gpio.IN, pull_up_down=gpio.PUD_UP)

last_time = time.time()
speed = 0.0
rps = 4.0

def when_low(channel):
    global speed
    global last_time
    global rps
    now = time.time()
    dt = now - last_time
    speed = (2.0 * 3.14) / (dt * rps)
    last_time = now

gpio.setmode(gpio.BCM)
gpio.setup(20, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.add_event_detect(20, gpio.FALLING, callback=when_low)

for i in range(0, 1000):
    print speed
    time.sleep(0.1)
gpio.cleanup()
