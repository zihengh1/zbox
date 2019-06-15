import os
import csv
import time
import math
import pigpio
import serial
import commands
import logging
from datetime import datetime

## lib module ##
import lib.zbox_config as Conf
import lib.G5_module as G5_m
import lib.ploting_module as plot_m
import lib.screen_modlue as screen_m

if __name__ == '__main__':

    ## set debug log file ##
    logging.basicConfig(filename="/home/pi/zbox/debug.log", format='%(asctime)s - %(levelname)s - %(message)s', filemode='w', datefmt='%Y-%m-%d %H:%M:%S')
    
    ## creating an logging object ##
    logger = logging.getLogger() 
  
    ## setting the threshold of logger to DEBUG ##
    logger.setLevel(logging.DEBUG) 

    ## initial PIGPIO library ##
    (s, process) = commands.getstatusoutput('sudo pidof pigpiod')
    
    if s:
        logger.warning("pigpiod was not running")
        commands.getstatusoutput('sudo pigpiod')
        time.sleep(0.1)

    if not s:
        logger.info("pigpio is running, process ID is %s", process)
    
    pi = pigpio.pi()
    logger.info("start to sense environment")
    sense_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S").split(" ")
    sense_data = Conf.device_info.copy()

    sense_data["date"] = str(sense_time[0])
    sense_data["time"] = str(sense_time[1])
    sense_data["device_id"] = Conf.DEVICE_ID
    sense_data["tick"] = Conf.tick
     
    logger.info("==================================")

    ########## CO2 Part ##########
    if(os.path.exists("/dev/ttyUSB0")):
        logger.info("s8 port exist")
        co2_serial = serial.Serial("/dev/ttyUSB0", baudrate = 9600, timeout = 0.5)
        co2_serial.flushInput()
        co2_serial.write("\xFE\x44\x00\x08\x02\x9F\x25")
        time.sleep(0.5)
        co2_raw_data = co2_serial.read(7)
        high = ord(co2_raw_data[3])
        low = ord(co2_raw_data[4])
        co2 = (high * 256) + low
        logger.info("@@ CO2 DATA: %s", str(co2))
        sense_data["s_g8"] = co2
        co2_serial.close()
        logger.info("s8 port close successfully")
    else:
        logger.error("s8 port doesn't exist")
    #############################

    logger.info("==================================")

    ########## PM2.5 Part ##########
    try:
        pi.bb_serial_read_close(Conf.G5_GPIO)
    except Exception:
        pass
    
    logger.info("G5 port has already closed")
    
    try:
        pi.bb_serial_read_open(Conf.G5_GPIO, 9600)
        time.sleep(1)
        (status, pm25_raw_data) = pi.bb_serial_read(Conf.G5_GPIO)
        if status:
            logger.info("G5 read data successfully")
            hex_data = G5_m.bytes2hex(pm25_raw_data)
            (check, pm1, pm25, pm10) = G5_m.read_data(hex_data)
            if check:
                logger.info("@@ PM1.0 DATA: %s", str(pm1))
                logger.info("@@ PM2.5 DATA: %s", str(pm25))
                logger.info("@@ PM10 DATA: %s", str(pm10))
                sense_data["s_d0"] = pm25
                sense_data["s_d1"] = pm10
                sense_data["s_d2"] = pm1
            else:
                logger.error("G5 occur missing data") 
        else:
            logger.error("G5 read data failed")

    except Exception as e:
        logger.error("G5 port open failed, error msg: %s", e) 

    try:
        pi.bb_serial_read_close(G5_GPIO)
    except Exception:
        pass
    
    logger.info("G5 port close successfully")
    ##############################

    logger.info("==================================")

    ########## Temp & Hum Part ##########
    try:    
        htu_handle = pi.i2c_open(1, Conf.htu_address)
        pi.i2c_write_byte(htu_handle, Conf.htu_reset)
        pi.i2c_close(htu_handle)
        logger.info("HTU21 initial successfully")
        time.sleep(0.1)
    except Exception as e:
        logger.error("HTU21 initial failed, error msg: %s", e)
    
    try:
        htu_handle = pi.i2c_open(1, Conf.htu_address)
        pi.i2c_write_byte(htu_handle, Conf.htu_rdtemp)
        time.sleep(0.055)
        (status_t, temp_raw_data) = pi.i2c_read_device(htu_handle, 3)
       
        if status_t > 0: 
            logger.info("HTU21 read tmp data sucessfully")
            t1 = temp_raw_data[0]
            t2 = temp_raw_data[1]
            tmp = (t1 * 256) + t2
            tmp = ((math.fabs(tmp) / 65536) * 175.72) - 46.85
            logger.info("@@ TMP DATA: %s", str(tmp))
            sense_data["s_t0"] = int(tmp)
        else:
            logger.info("HTU21 read tmp data failed")
        pi.i2c_close(htu_handle)
        logger.info("HTU21 tmp port close successfully")
            
        htu_handle = pi.i2c_open(1, Conf.htu_address)
        pi.i2c_write_byte(htu_handle, Conf.htu_rdhum)
        time.sleep(0.055)
        (status_h, hum_raw_data) = pi.i2c_read_device(htu_handle, 3)
       
        if status_h > 0:
            logger.info("HTU21 read hum data successfully")
            h1 = hum_raw_data[0]
            h2 = hum_raw_data[1]
            hum = (h1 * 256) + h2
            uncomp_hum = ((math.fabs(hum) / 65536) * 125) - 6
            com_hum = ((25 - tmp) * (-0.15)) + uncomp_hum
            logger.info("@@ HUM DATA: %s", str(com_hum))
            sense_data["s_h0"] = int(com_hum)
        else:
            logger.info("HTU21 read hum data failed")
        pi.i2c_close(htu_handle)
        logger.info("HTU21 hum port close successfully")
         
    except Exception as e:
        logger.error("HTU21 open failed, error msg: %s", e)
    ###################################

    logger.info("==================================")

    ########## Light Part #############
    try:
        tcs_handle = pi.i2c_open(1, 0x29)
        pi.i2c_write_device(tcs_handle, b'\x29\x80\x03')
        pi.i2c_write_device(tcs_handle, b'\x29\x81\x00')
        pi.i2c_write_device(tcs_handle, b'\x29\x83\xFF')
        pi.i2c_write_device(tcs_handle, b'\x29\x8F\x00')
        (status_c, color_raw_data) = pi.i2c_read_device(tcs_handle, 8)
        if status_c > 0:
            logger.info("TCS read data successfully")
            c = color_raw_data[1] * 256 + color_raw_data[0]
            r = color_raw_data[3] * 256 + color_raw_data[2]
            g = color_raw_data[5] * 256 + color_raw_data[4]
            b = color_raw_data[7] * 256 + color_raw_data[6]
            l = (-0.32466 * r) + (1.57837 * g) + (-0.73191 * b)
            logger.info("@@ C DATA: %s", str(c))
            logger.info("@@ R DATA: %s", str(r))
            logger.info("@@ G DATA: %s", str(g))
            logger.info("@@ B DATA: %s", str(b))
            logger.info("@@ L DATA: %s", str(l))
            sense_data["s_l0"] = int(l)
            sense_data["s_lr"] = r
            sense_data["s_lg"] = g
            sense_data["s_lb"] = b
            sense_data["s_lc"] = c

        else:
            logger.error("TCS read data failed")
        
        pi.i2c_close(tcs_handle)
        logger.info("TCS port close successfully")

    except Exception as e:
        logger.error("TCS open failed error msg: %s", e)
    ###################################        

    print(sense_data)

    ########## Store Data #############

    info_key = sense_data.keys()
    store_data = [sense_data]
    
    if os.path.exists(Conf.data_path + "record.csv") is False:
        logger.info("Write a new record")
        with open(Conf.data_path + "record.csv", "a") as output_file:
            dict_writer = csv.DictWriter(output_file, info_key)
            dict_writer.writeheader()
         
    with open(Conf.data_path + "record.csv", "a") as output_file:
        try:
            dict_writer = csv.DictWriter(output_file, info_key)
            dict_writer.writerows(store_data)
            logger.info("Storing data successfully") 
        except Exception as e:
            logger.error("Storing data failed, error msg: %s", e) 

    ###################################

    logger.info("==================================")
    
    ########## Display Part ###########
    try:
        plot_m.draw() 
        logger.info("Draw pm2.5 line plot successfully")
    except Exception as e:
        logger.error("Draw pm2.5 line plot failed, error msg: %s", e)

    try:
        screen_m.transform_to_bmp()
        screen_m.display(sense_data)
        logger.info("Display successfully")
    except Exception as e:
        logger.error("Display failed")

    ################################### 
    
    logger.info("==================================")
    logger.info("Sense Over")
    pi.stop()



























