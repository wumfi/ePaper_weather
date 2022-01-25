from functions import *
from machine import lightsleep, sleep, RTC
sleepytime=300 * 1000
global epd
epd = Eink(rotation=270, cs_pin=36, dc_pin=14, reset_pin=8, busy_pin=9)
while True:
    ConnectToWifi()
    debug("Updating screen")
    UpdateEPD(epd)
    ShutdownWifi()
    sleep(sleepytime)

#Leaving this here for debug/testing
# ConnectToWifi()
# debug("Updating screen")
# UpdateEPD(epd)
# ShutdownWifi()