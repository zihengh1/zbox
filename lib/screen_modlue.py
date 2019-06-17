import re
import time
import json
import traceback
import commands
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from urllib2 import urlopen

from zbox_config import plot_path
import epaper.epd2in7 as epd2in7

def transform_to_bmp():
    file_in = plot_path + "pm25_line.png"
    file_out = plot_path + "pm25_line.bmp"

    img = Image.open(file_in)
    img = img.convert("L")
    img = img.resize((264, 130), Image.ANTIALIAS)
    img.save(file_out)

def get_city():
    url = "http://ipinfo.io/json"
    try:
        response = urlopen(url)
        info = json.load(response)
        city = info['city']
        return city
    except:
        return "X"
    
def display(data):
    
    try:
        epd = epd2in7.EPD()

        ## Initialize ##
        epd.init()

        ## Clear screen ##
        epd.Clear(0xFF)

        ## Drawing information ##
        Himage1 = Image.new('1', (epd2in7.EPD_HEIGHT, epd2in7.EPD_WIDTH), 255)
        draw = ImageDraw.Draw(Himage1)
        font_size = ImageFont.truetype('/usr/share/fonts/truetype/ttf-bitstream-vera/Vera.ttf',11)

        ## String format ##        
        app = data["app"]
        city = get_city()
        device_id = data["device_id"]
        pm25 = "PM2.5: " + str(data["s_d0"])
        hum = "Hum: " + str(data["s_h0"])
        temp = "Tmp: " + str(data["s_t0"])
        co2 = "CO2: " + str(data["s_g8"])
        light = "Lux: " + str(data["s_l0"])
        r = "R: " + str(data["s_lr"])
        g = "G: " + str(data["s_lg"])
        b = "B: " + str(data["s_lb"])
        ip = commands.getoutput('hostname -I')
        time_str = data["date"] + " " + data["time"]
        
        ## Draw text ##
        draw.text((3, 0), app, font = font_size, fill = 0)
        draw.text((75, 0), city, font = font_size, fill = 0)
        draw.text((173, 0), device_id, font = font_size, fill = 0)
        
        draw.text((3, 11), pm25, font = font_size, fill = 0)
        draw.text((75, 11), co2, font = font_size, fill = 0)
        draw.text((147, 11), hum, font = font_size, fill = 0)
        draw.text((215, 11), temp, font = font_size, fill = 0)
        
        draw.text((3, 22), light, font = font_size, fill = 0)
        draw.text((75, 22), r, font = font_size, fill = 0)
        draw.text((147, 22), g, font = font_size, fill = 0)
        draw.text((215, 22), b, font = font_size, fill = 0) 

        draw.text((3, 33), time_str, font = font_size, fill = 0)
        draw.text((172, 33), ip, font = font_size, fill = 0)

        draw.line((3, 45, 260, 45), fill = 0)
      
        bmp = Image.open(plot_path + 'pm25_line.bmp')
        Himage1.paste(bmp, (0,47))
       
        ## Display ##
        epd.display(epd.getbuffer(Himage1))
        
        ## Sleep ##
        epd.sleep()
        
    except Exception as e:
        print(e)

