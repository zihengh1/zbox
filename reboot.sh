#!/bin/bash

sleep 5 
[ -f /home/pi/AirBox2/sense.py ] && {
    /usr/bin/sudo git -C /home/pi/AirBox2 fetch origin
    /usr/bin/sudo git -C /home/pi/AirBox2 reset --hard origin/master
    /usr/bin/python /home/pi/AirBox2/sense.py > /home/pi/AirBox2/ans.txt
    echo ok1 > /home/pi/AirBox2/config.txt
} || {
    /usr/bin/sudo git clone https://github.com/zihengh1/AirBox2.git /home/pi/AirBox2
    echo ok2 > /home/pi/AirBox2/config.txt
}
