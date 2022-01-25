from functions import *
from machine import deepsleep, sleep
sleepytime=300 * 1000

# while True:
#     ConnectToWifi()
#     debug("Done")
#     debug("Trying to get time from NTP")
#     try:
#         settime() # Grab NTP time
#         debug("Success - written to RTC")
#     except:
#         debug("Bugger, that failed!")
#         pass
# 
#     debug("Updating screen")
#     UpdateEPD()
#     ShutdownWifi()
#     sleep(60000)
    
ConnectToWifi()
debug("Done")
debug("Trying to get time from NTP")
try:
    settime() # Grab NTP time
    debug("Success - written to RTC")
except:
    debug("Bugger, that failed!")
    pass

debug("Updating screen")
UpdateEPD()
ShutdownWifi()
