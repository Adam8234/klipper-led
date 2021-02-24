# klipper-led

## Wiring Instuctions
Wire data pin to GPIO 18, PCM_CLK pin on the raspberr PI. Make sure you share a common ground to the LEDs or they wont properly light. LEDs data in/out must be wired in series.

If you have a large amount of LEDs you should wire 5V seperately.

Reference this - https://learn.adafruit.com/neopixels-on-raspberry-pi/raspberry-pi-wiring for more wiring options

## Install Instructions

```
git clone https://github.com/Adam8234/klipper-led
cd ~/klipper-led
chmod +x ./install.sh
./install.sh
```

When prompted, put in your password...

## Config Instructions
You can edit this code in app.py. I have it configured for 3x16 NeoPixel rings.

possible LED types:
* LED_PROGRESS.EXTRUDER - Extruder Value
* LED_PROGRESS.HEATER_BED - Heater Value
* LED_PROGRESS.PROGRESS - SD Card Progress

```
leds = [
    {
        # Index of first led starting from zero (for example: index 0-15 will be taken with this led strand)
        'index': 0,
        'led_count': 16,
        'led_type': LED_PROGRESS.PROGRESS,
        'main_color': (0, 255, 0)  # RGB
    },
    {
        'index': 16,  # Index of first led starting from zero
        'led_count': 16,
        'led_type': LED_PROGRESS.HEATER_BED,
        'main_color': (255, 0, 0)  # RGB
    },
    {
        'index': 32,  # Index of first led starting from zero
        'led_count': 16,
        'led_type': LED_PROGRESS.EXTRUDER,
        'main_color': (0, 0, 255)  # RGB
    }
]
```
