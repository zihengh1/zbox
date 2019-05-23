#!/bin/bash

sleep 5 
[ -f /home/pi/AirBox2/sense.py ] && {
    /usr/bin/sudo git -C /home/pi/AirBox2 fetch origin
    /usr/bin/sudo git -C /home/pi/AirBox2 reset --hard origin/master
}
