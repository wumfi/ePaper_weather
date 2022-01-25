from config import *
from Pico_ePaper_partial import Eink
from writer import Writer
from utime import sleep_ms,gmtime
from ntptime import settime
from machine import deepsleep
from network import WLAN,STA_IF
from sys import path
from time import time,localtime
from ujson import loads
from urequests import get
from framebuf import FrameBuffer, MONO_HLSB
global WeatherJSON
global epoch_adjust
global epd
epoch_adjust=946684800

# Append our custom dirs to the path
path.append("/icons")
path.append("/fonts")
import ClearNight,Hot,Sun,CloudyNight,PartialCloud,Warm,Cold,Rain,Drizzle,Windy,Freezing,Snow,FullCloud,Storm,Foggy
import dinomouse20, dinomouse30, dinomouse40, freesans20

def ConnectToWifi():
    sta_if = WLAN(STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(ssid, pwd)
        while not sta_if.isconnected():
            pass
    settime()
    print('network config:', sta_if.ifconfig())

def ShutdownWifi():
    wifi = WLAN(STA_IF)
    wifi.active(False)
    print("Network diconnected")

debugflag=1

class DummyDevice(FrameBuffer):
    def __init__(self, width, height, buf_format):
        self.width = width
        self.height = height
        self._buf = bytearray(self.width * self.height // 8)
        super().__init__(self._buf, self.width, self.height, buf_format)
        self.fill(1)

# If x/y are not specified, then text will be centered in that axis across the whole screen
# Optional xoffset, xwidth, yoffset, yheight allows centering within boxes
# Logic is that if either x or y is missing, then it will centre in that axis.  Additionally,
# If offset and width is specified for an axis, then it will centre starting from offset and use width
def wstring(epd,text,fontname,x=None,y=None,xoffset=None,xwidth=None,yoffset=None,yheight=None):
    
    dummy = DummyDevice(epd.width, epd.height, MONO_HLSB)
    wri = Writer(dummy, fontname)
    
    if x==None:
        if xoffset==None:
            x=(epd.width - wri.stringlen(text)) // 2
        else:
            x=(xwidth - wri.stringlen(text)) // 2 + xoffset
    if y==None:
        if yoffset==None:
            y=(epd.height - wri.height) // 2
        else:
            y=(yheight - wri.height) // 2 + yoffset
    wri.set_clip(row_clip=True, col_clip=True, wrap=True)
    print(f"X={x} Y={y}")
    Writer.set_textpos(dummy, col=x, row=y)
    wri.printstring(text, invert=True)
    epd.blit(dummy, 0, 0, key=1, ram=epd.RAM_RBW)

# Same deal, see comments on previous function
def wimage(epd,icon,x=None,y=None,xoffset=None,xwidth=None,yoffset=None,yheight=None):
    if x==None:
        if xoffset==None:
            x=(epd.width - icon.width) // 2
        else:
            x=(xwidth - icon.width) // 2 + xoffset
    if y==None:
        if yoffset==None:
            y=(epd.height - icon.height) // 2
        else:
            y=(yheight - icon.height) // 2 + yoffset
    img_tmp = FrameBuffer(icon.img_bw, icon.width, icon.height, MONO_HLSB)
    # Blit img_bw to BW RAM.
    epd.blit(img_tmp, x, y, ram=epd.RAM_BW)
    # Reuse img_tmp to load img_red.
    img_tmp = FrameBuffer(icon.img_red, icon.width, icon.height, MONO_HLSB)
    # And blit it to RED RAM at the same position as previous blit.
    epd.blit(img_tmp, x, y, ram=epd.RAM_RED)

def GetWeather():
    global WeatherJSON
    response = get("http://api.openweathermap.org/data/2.5/onecall?lat=50.967779&lon=-0.114799&appid="+apiKey+"&units=metric")
    WeatherJSON=loads(response.content)

def GetSuffix(daynum):
    #last=daynum[-1]
    if daynum=="1":
        return "st"
    elif daynum=="2":
        return "nd"
    elif daynum=="3":
        return "rd"
    else:
        return "th"

def GetDTBit(epoch,whichbit):
    # Convert the epoch to a real date
    # Note, this board uses Jan 1 2000 rather than the normal 1970 one hence the - 946684800 bit in other functions
    # Note, this tuple has 8 parts, and the last two are DOY and DOW (Monday = 0)
    # ex. (2022, 1, 20, 21, 13, 31, 3, 20)
    # Various cases then return the relevant bits as needed
    global epoch_adjust
    real = localtime(epoch-epoch_adjust)
    monthdict={1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
    title=str(real[2])+GetSuffix(str(real[2]))+" "+str(monthdict[real[1]])+" "+str(real[0])

    if whichbit=="d":
        return str(real[2])
    elif whichbit=="o":
        return str(monthdict[real[1]])
    elif whichbit=="y":
        return str(real[0])
    elif whichbit=="h":
        return str(real[3])
    elif whichbit=="m":
        return str(real[4])
    elif whichbit=="dt":
        return title
    elif whichbit=="tm":
        if real[4]<10:
            return str(real[3])+":0"+str(real[4])
        else:
            return str(real[3])+":"+str(real[4])

def GetIcon(cond,h=None,typ=None):
    # 200-thunder, 300-drizzle, 500-rain, 600-snow, 700-atmos (fog etc.), 800-clear, 801-25%, 802-50%, 803-84%, 804-overcast
    # Need to sort ntp here so we know if it's nightime
    if typ=="weather":
        IconDict={}
        if cond < 300: # Thunder 200-299, there is no 100
            return Storm
        elif cond <400: # Drizzle 300-399:
            return Drizzle
        elif cond <600: # Rain 500-599, there is no 400
            return Rain
        elif cond <700: # Snow 600
            return Snow
        elif cond <800: # Fog etc. 700
            return Foggy
        elif cond == 800: # Clear day
            if h > 18 or h < 8:
                return ClearNight
            else:
                return Sun
        elif cond == 801 or cond == 802 or cond == 803:
            return PartialCloud
        elif cond == 804:
            return FullCloud
    else:
        if cond<5:
            return Freezing
        elif cond<15:
            return Cold
        elif cond<25:
            return Warm
        else:
            return Hot
    
def debug(msg):
    if debugflag==1:
        print(msg)
        
def SetBackground(epd):
    epd.rect(0,0,480,280)
    epd.hline(0,56,480)
    epd.vline(138,56,240)

def SetTopPane(epd):
    global epoch_adjust
    wstring(epd=epd,text=f"{GetDTBit(time()+epoch_adjust,"dt")}",yoffset=0,yheight=60,fontname=dinomouse40)

def SetLeftPane(epd):
    global WeatherJSON
    global epoch_adjust
    current_hour=int(GetDTBit(time()+epoch_adjust,"h"))
    current_min=int(GetDTBit(time()+epoch_adjust,"m"))
    if current_hour>0 and current_hour<13:
        suffix="am"
    else:
        current_hour-=12
        suffix="pm"
    wstring(epd=epd,text=f"{GetFriendlyTime(GetDTBit(time()+epoch_adjust,"tm"))}",xoffset=0,xwidth=138,y=72,fontname=freesans20)
    icon=GetIcon(cond=WeatherJSON["current"]["weather"][0]["id"],h=gmtime()[3],typ="weather")
    wimage(epd=epd,icon=icon,xoffset=0,xwidth=138,y=92)
    wstring(epd=epd,text=icon.desc,xoffset=0,xwidth=138,y=150,fontname=freesans20)
    icon=GetIcon(cond=WeatherJSON["current"]["feels_like"])
    wimage(epd=epd,icon=icon,xoffset=0,xwidth=138,y=180)
    wstring(epd=epd,text=f"{round(WeatherJSON["current"]["feels_like"])} c",xoffset=0,xwidth=138,y=250,fontname=freesans20)
    
    
def SetMainPane(epd):
    global WeatherJSON
    ctr=1
    DictWeather={}
    for h in range(3,10,3):
        DictWeather[ctr]={"dt": GetDTBit(WeatherJSON["hourly"][h]["dt"],"tm"), "code": WeatherJSON["hourly"][h]["weather"][0]["id"], "temp": round(WeatherJSON["hourly"][h]["feels_like"])}
        ctr += 1
    for h in range(1,4):
        this_hour=int(DictWeather[h]["dt"].split(":")[0])
        icon=GetIcon(cond=DictWeather[h]["code"],h=this_hour,typ="weather")
        wimage(epd=epd,icon=icon,yoffset=92,yheight=60,x=80+(h*100))
        wstring(epd=epd,text=GetFriendlyTime(DictWeather[h]["dt"]),xoffset=80+(h*100),xwidth=icon.width,yoffset=142,yheight=60,fontname=freesans20)
        wstring(epd=epd,text=icon.desc,xoffset=80+(h*100),xwidth=icon.width,yoffset=180,yheight=60,fontname=dinomouse20)
        wstring(epd=epd,text=f"{DictWeather[h]["temp"]} c",xoffset=80+(h*100),xwidth=icon.width,yoffset=200,yheight=60,fontname=freesans20)

def GetFriendlyTime(dt):
    print(dt)
    h=int(dt.split(":")[0])
    m=dt.split(":")[1]
    if h == 0:
        return "Midnight"
    elif h < 13:
        return f"{h}:{m}am"
    else:
        return f"{h-12}:{m}pm"

def UpdateEPD(epd):
    GetWeather()
    epd.fill()
    SetBackground(epd)
    SetTopPane(epd) 
    SetLeftPane(epd)
    SetMainPane(epd)
    epd.show()
    #epd.sleep()