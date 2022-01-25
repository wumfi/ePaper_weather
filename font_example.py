# Demo for using Writer class to render text in fonts not directly supported by FrameBuffer class.

# dinomouses example relies on micropython-font-to-py utility and Writer class by Peter Hinch:
# https://github.com/peterhinch/micropython-font-to-py. For details on usage please refer to documentation provided
# in that repository.
# To use dinomouses example make sure files writer.py and dinomouse.py are present on flash along example file.

from Pico_ePaper import Eink
import framebuf
from writer import Writer
import time
from utime import sleep_ms
import sys
sys.path.append("/icons")
sys.path.append("/fonts")
import dinomouse
import test as imagefile

title = "Our weather!"

class DummyDevice(framebuf.FrameBuffer):
    def __init__(self, width, height, buf_format):
        self.width = width
        self.height = height
        self._buf = bytearray(self.width * self.height // 8)
        super().__init__(self._buf, self.width, self.height, buf_format)
        self.fill(1)

def wstring(txt,x,y):
    dummy = DummyDevice(epd.width, epd.height, framebuf.MONO_HLSB)
    wri = Writer(dummy, dinomouse)
    wri.set_clip(row_clip=True, col_clip=True, wrap=True)
    wri.printstring(txt, invert=True)
    Writer.set_textpos(dummy, 0, 0)
    epd.blit(dummy, x, y, key=1)

    
def wimage(x,y):
    img_tmp = framebuf.FrameBuffer(imagefile.img_bw, imagefile.width, imagefile.height, framebuf.MONO_HLSB)
    # Blit img_bw to BW RAM.
    epd.blit(img_tmp, int(240-(int(imagefile.width)/2)), 80, ram=epd.RAM_BW)
    # Reuse img_tmp to load img_red.
    img_tmp = framebuf.FrameBuffer(imagefile.img_red, imagefile.width, imagefile.height, framebuf.MONO_HLSB)
    # And blit it to RED RAM at the same position as previous blit.
    epd.blit(img_tmp, int(240-(int(imagefile.width)/2)), 80, ram=epd.RAM_RED)
    
def dobackground():
    epd.rect(0,0,480,280)
    epd.rect(6,6,468,268)
    epd.line(6,60,474,60)
    
epd = Eink(rotation=270)
epd.partial_mode_on()
epd.fill
dobackground()
wimage(0,0)

wstring(title,138,18)
epd.show()
epd.partial_mode_off()
epd.sleep()