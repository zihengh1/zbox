#!/bin/bash

OTA="https://github.com/zihengh1/AirBox2.0.git"

sleep 5 
[ -f /home/pi/AirBox2.0/main_sense.py ] && {
    /usr/bin/sudo git -C /home/pi/AirBox2.0 fetch --all
    /usr/bin/sudo git -C /home/pi/AirBox2.0 reset --hard origin/master
    /usr/bin/python /home/pi/AirBox2.0/main_sense.py > /home/pi/AirBox2.0/ans.txt
} || {
    /usr/bin/sudo git clone OTA /home/pi/AirBox2.0
}
