#!/bin/bash

sleep 5 
[ -f /home/pi/AirBox2/sense.py ] && {
    /usr/bin/sudo git -C /home/pi/zbox fetch origin
    /usr/bin/sudo git -C /home/pi/zbox reset --hard origin/master
}
