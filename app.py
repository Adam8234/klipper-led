#!/usr/bin/env python3
import requests
import json
import serial

serial.Serial(
    port='/dev/serial/by-id/usb-Arduino_LLC_Arduino_Leonardo-if00',
    baudrate=57600,
)

resp = requests.get("http://127.0.0.1/printer/objects/query?webhooks&virtual_sdcard&extruder&heater_bed")
respDict = json.loads(resp.text)
print(respDict["result"]["status"]["virtual_sdcard"])



