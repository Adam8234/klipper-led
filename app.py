#!/usr/bin/env python3
import requests
import json
import board
import neopixel
import enum
import _thread
import time


class LED_PROGRESS(enum.Enum):
    EXTRUDER = 1
    HEATER_BED = 2
    PROGRESS = 3


class STATE(enum.Enum):
    ERROR = -1
    START_UP = 1
    IDLE = 2
    PRINTING = 3


global brightness_direction

state_startup_brightness_direction = float(-0.025)
state_virual_sdcard_active = False
state_webhook_state = "ready"

state_printer_max_extruder_temp = 0
state_printer_max_heater_bed_temp = 0
state_printer_extruder_temp = 0
state_printer_heater_bed_temp = 0
state_printer_extruder_taget_temp = 0
state_printer_heater_bed_taget_temp = 0
state_idle_brightness = 1.0
state_virual_sdcard_progress = 0.0

state = STATE.START_UP

leds = [
    {
        'index': 0,
        'led_count': 16,
        'led_type': LED_PROGRESS.PROGRESS,
        'main_color': (255, 0, 0)
    },
    {
        'index': 16,
        'led_count': 16,
        'led_type': LED_PROGRESS.HEATER_BED,
        'main_color': (0, 255, 0)
    },
    {
        'index': 32,
        'led_count': 16,
        'led_type': LED_PROGRESS.EXTRUDER,
        'main_color': (0, 255, 0)
    }
]

total_leds = 0
for led in leds:
    total_leds += led["led_count"]
pixels = neopixel.NeoPixel(board.D18, total_leds, auto_write=False)


def update_leds_periodic():
    global state_startup_brightness_direction, state_idle_brightness
    pixels.fill((0, 0, 0))
    while 1:
        if(state == STATE.START_UP):
            pixels.brightness = pixels.brightness + state_startup_brightness_direction
            if(pixels.brightness >= 1.0):
                state_startup_brightness_direction *= -1
            elif(pixels.brightness <= 0):
                state_startup_brightness_direction *= -1
            pixels.fill((255, 255, 255))
        elif(state == STATE.ERROR):
            pixels.brightness = 1.0
            pixels.fill((255, 0, 0))
        elif(state == STATE.IDLE):
            pixels.brightness = 1.0
            for led in leds:
                if(led["led_type"] == LED_PROGRESS.PROGRESS):
                    for i in range(led["index"], led["index"] + led["led_count"]):
                        pixels[i] = (int(255 * state_idle_brightness),
                                     int(255 * state_idle_brightness),
                                     int(255 * state_idle_brightness))
                    state_idle_brightness = state_idle_brightness + state_startup_brightness_direction
                    if(state_idle_brightness >= 1.0):
                        state_idle_brightness = 1.0
                        state_startup_brightness_direction *= -1
                    elif(state_idle_brightness <= 0):
                        state_idle_brightness = 0
                        state_startup_brightness_direction *= -1
        elif(state == STATE.PRINTING):
            for led in leds:
                if(led["led_type"] == LED_PROGRESS.PROGRESS):
                    temperature_index = int(
                        led["led_count"] * state_virual_sdcard_progress)
                    for i in range(led["index"], led["index"] + temperature_index):
                        pixels[i] = led["main_color"]
        if(state == STATE.IDLE or state == STATE.PRINTING):
            for led in leds:
                if(led["led_type"] == LED_PROGRESS.EXTRUDER):
                    temperature_index = int(
                        led["led_count"] * (state_printer_extruder_temp / state_printer_max_extruder_temp))
                    target_temperature_index = int(
                        led["led_count"] * (state_printer_extruder_target_temp / state_printer_max_extruder_temp))
                    for i in range(led["index"], led["index"] + temperature_index):
                        pixels[i] = led["main_color"]

                    if(target_temperature_index > temperature_index):
                        pixels[target_temperature_index + led["index"]
                               ] = tuple(int(0.25 * x)for x in led["main_color"])
                elif(led["led_type"] == LED_PROGRESS.HEATER_BED):
                    temperature_index = int(
                        led["led_count"] * (state_printer_heater_bed_temp / state_printer_max_heater_bed_temp))
                    target_temperature_index = int(
                        led["led_count"] * (state_printer_heater_bed_target_temp / state_printer_max_heater_bed_temp))
                    for i in range(led["index"], led["index"] + temperature_index):
                        pixels[i] = led["main_color"]

                    if(target_temperature_index > temperature_index):
                        pixels[target_temperature_index + led["index"]
                               ] = tuple(int(0.25 * x)for x in led["main_color"])

        pixels.show()
        time.sleep(0.0083)


_thread.start_new_thread(update_leds_periodic, ())


def change_state(new_state):
    global state
    pixels.fill((0, 0, 0))
    if(state != new_state):
        state_idle_brightness = 0.0
        print("Changing from ", state, " to ",  new_state)
        state = new_state


time.sleep(2)
while 1:
    resp = requests.get(
        "http://127.0.0.1/printer/objects/query?webhooks&virtual_sdcard&extruder&heater_bed&configfile")
    if(resp.status_code != 200):
        change_state(STATE.ERROR)
    else:
        respDict = json.loads(resp.text)["result"]["status"]

        state_virual_sdcard_active = respDict["virtual_sdcard"]["is_active"]
        state_virual_sdcard_progress = respDict["virtual_sdcard"]["progress"]
        state_webhook_state = respDict["webhooks"]["state"]

        state_printer_extruder_temp = respDict["extruder"]["temperature"]
        state_printer_heater_bed_temp = respDict["heater_bed"]["temperature"]
        state_printer_extruder_target_temp = respDict["extruder"]["target"]
        state_printer_heater_bed_target_temp = respDict["heater_bed"]["target"]
        state_printer_max_extruder_temp = respDict["configfile"]["settings"]["extruder"]["max_temp"]
        state_printer_max_heater_bed_temp = respDict["configfile"]["settings"]["heater_bed"]["max_temp"]

        if(state_webhook_state == "ready"):
            if(state_virual_sdcard_active != True):
                change_state(STATE.IDLE)
            else:
                change_state(STATE.PRINTING)
    time.sleep(1)
