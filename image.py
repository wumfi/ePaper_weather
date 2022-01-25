from Pico_ePaper import Eink
import framebuf
from utime import ticks_ms, ticks_diff

# Import image files
import tux as img2

epd = Eink(rotation=270)
epd.fill()

# Grayscale image.
# Load img_bw to temporary framebuffer.
img_tmp = framebuf.FrameBuffer(img2.img_bw, img2.width, img2.height, framebuf.MONO_HLSB)
# Blit img_bw to BW RAM.
epd.blit(img_tmp, 0, 0, ram=epd.RAM_BW)
# Reuse img_tmp to load img_red.
img_tmp = framebuf.FrameBuffer(img2.img_red, img2.width, img2.height, framebuf.MONO_HLSB)
# And blit it to RED RAM at the same position as previous blit.
epd.blit(img_tmp, 0, 0, ram=epd.RAM_RED)
# Show images and put display controller to sleep.
#epd.fill()
epd.show()
epd.sleep()
