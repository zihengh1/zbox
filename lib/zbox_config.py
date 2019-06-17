import re
import commands

## GPIO setting ##
G5_GPIO = 23

## HTU21D Command
htu_address     = 0x40
htu_rdtemp      = 0xE3
htu_rdhum       = 0xE5
htu_reset       = 0xFE

## TCS34725 Command
tcs_address     = 0x29

## IP address ##
DEVICE_IP = commands.getoutput("hostname -I")

## MAC address ##
mac = open('/sys/class/net/eth0/address').readline().upper().strip()
DEVICE_ID = mac.replace(':','') 

## Tick time
with open('/proc/uptime', 'r') as f:
    try:
        tick = float(f.readline().split()[0])
    except:
        print "Error: reading /proc/uptime"

## Screen display 
plot_path = "/home/pi/zbox/PLOT/"

## Store data path
data_path = "/home/pi/Data/"

## Upload url 
Restful_URL = "https://pm25.lass-net.org/Uploads/PiM25.php?"

## Device information
device_info = { "s_d0"      : -1, \
                "s_d1"      : -1, \
                "s_d2"      : -1, \
                "s_t0"      : -1, \
                "s_h0"      : -1, \
                "s_l0"      : -1, \
                "s_lr"      : -1, \
                "s_lg"      : -1, \
                "s_lb"      : -1, \
                "s_lc"      : -1, \
                "s_g8"      : -1, \
                "date"      : "", \
                "time"      : "", \
                "gps_num"   : 0, \
                "gps_lat"   : 25.1933, \
                "gps_lon"   : 121.7870, \
                "app"       : "PiM25", \
                "device"    : "Raspberry_Pi", \
                "device_id" : "", \
                "tick"      : -1, \
                "fmt_opt"   : 0, \
                "ver_format": 3, \
                "gps_fix"   : 0, \
                "ver_app"   : "0.0.1", \
                "FAKE_GPS"  : 0
              }

