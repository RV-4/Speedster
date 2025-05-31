#!/usr/bin/env python
# Run on Pi-Zero with 2" ePaper display hat called "PaPiRus"

# /home/pi/1TM/serial-papirus.py

#  Version 2.a
print("serial-papirus.py Version 2.0a")


# Power Raspberry Pi Zero via Micro-USB in USB port.
# Modify /boot/cmdline.txt
#    Add "modules-load=dw2" after "rootwait"
# Modify /boot/confix.txt
#    Add "dtoverlay=dwc2" at the end of the file
# Run Raspi-Config to enable serial ports and disable login console over serial
# The above will create a Serial instance on the USB cable via the "/dev/ttyGS0" driver
# The host USB will see a serial-USB device (/dev/ttyACM0) on a Raspberry Pi.
# Retrieve host IP address and gateway address and write to PaPiRus display

#   To setup micro-USB:
#    sudo systemctl enable getty@ttyGS0.service
#    sudo systemctl is-active getty@ttyGS0.service

# Program will read from OTG serial port connected to Automationhat Pi
# Format of data stream is:
# !41+ssssGhhhhhfff
# "+ssssG"   is the amount of smoke oil remaining in tenths of gallons
# "yyyyy"    is the Total Time (Hobbs Time) in tenths of hours from Dynon EMS
# "fff"      is the Total Fuel Remaining in tents of gallons

# !51aaa.bbb.ccc.ddd   IP Address of Automationhat Pi

# Run this line and PaPiRus will be setup and installed
#   curl -sSL https://pisupp.ly/papiruscode | sudo bash
#   Select "Python3"
#   Set screen size to 2.0

# To change screen size run:
#   sudo papirus-set [1.44 | 1.9 | 2.0 | 2.6 | 2.7 ]   -or-
#   sudo papirus-config



# To run at boot must have entry in /etc/rc.local
# sudo python3 /home/zap/Speedster/serial-papirus.py &

import socket
import os
from time import sleep
import serial
import time
from papirus import PapirusTextPos

print("Waiting for PaPiRus display and USB OTG to be ready")
sleep(5)

#  2" PaPiRus Display size is:  200 X 96 pixels
#text.AddText("N221TM",      30,  0, 39, Id="Line-1")
#text.AddText("SMOKE TANK",  10, 36, 30, Id="Line-2")    38, 30
#text.AddText("BOOTING",     15, 60, 39, Id="Line-3")    66, 30

try:
    text = PapirusTextPos(True)
except:
    print("Error: Unable to initialize PapirusTextPos.  Display not attached?\r\n   Program will exit")
    exit()

text.Clear()
time.sleep(1.0)

text.AddText("N221TM",     0,  0, 39)
text.AddText("SMOKE TANK", 0, 37, 30)
text.AddText("BOOTING",    0, 66, 30)
text.WriteAll()
time.sleep(10.0)

try:
    text.Clear()
    time.sleep(1.0)
    gw = os.popen("ip -4 route show default").read().split()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((gw[2], 0))
    ipaddr = s.getsockname()[0]
    gateway = gw[2]
    host = socket.gethostname()
    print ("IP:", ipaddr, " GW:", gateway, " Host:", host)
except:
    print("Error: Unable to get IP address")

#                      coll, row, height
text.AddText("N221TM ",0,  0, 39, Id="Line-1-Addr")
text.AddText(host,      0, 39, 25, Id="Line-2-Addr")
text.AddText(ipaddr,    0, 65, 25, Id="Line-3-Addr")

text.WriteAll()
time.sleep(10.0)



# Define serial link to Automationhat via USB OTG cable
try:
    automationhat_serial = serial.Serial(
        port='/dev/ttyGS0',
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=5
    )
except serial.SerialException:
    print("Error: Unable to open serial port")
    exit()

last_fuel =  100.1
last_smoke = 100.1
last_hobbs = 100.1
hobbs      = 200.1
smoke_gal  = 200.1
fuel       = 200.1
update     = False
loop_count = 0

# automationhat_serial.flushInput()                      # Flush input
# automationhat_bytes = automationhat_serial.read_until(b'\r\n', None)

text.Clear()
time.sleep(1.0)
text.AddText(" N221TM",    0,  0, 39, Id="Line-1")
text.AddText("  RV 4.5 ",  0, 37, 30, Id="Line-2")
text.AddText(" Speedster", 0, 66, 30, Id="Line-3")
text.WriteAll()
time.sleep(1.0)

while True:
    automationhat_bytes = automationhat_serial.read_until(b'\r\n', None)
#    automationhat_bytes = automationhat_serial.readline()
    print(automationhat_bytes)
    automationhat_str = automationhat_bytes.decode()
    automationhat_str.strip()
    print(automationhat_str)
    print()


    smoke_str = automationhat_str[3:9]
    hobbs_str = automationhat_str[9:14]
    fuel_remain_str = automationhat_str[14:17]

    print('Smoke Level: ',   smoke_str, ' Gallons')
    print('Total Time: ',    hobbs_str, ' Hours')
    print('Fuel Remaining:', fuel_remain_str, ' Gallons', end='\r\n\n')

    try:
        smoke_gal = float(automationhat_bytes[4:8]) / 10
        print('Smoke Level:', '{0:3.1f}' .format(smoke_gal), 'Gallons')
        smoke_change = abs(smoke_gal - last_smoke)
        if smoke_change > 0:
            gallonsF = "{:.1f}".format(smoke_gal)
            gallonsF = gallonsF + "  Smoke"
            if smoke_gal < 0.5: gallonsF = "-EMPTY-"
            text.UpdateText("Line-3", gallonsF)
            print("GallonsF:", gallonsF)
            last_smoke = smoke_gal
            update = True
    except ValueError:
        print()

    try:
        fuel = float(automationhat_bytes[14:17]) / 10
        print ('Fuel Level:', '{0:3.1f}' .format(fuel), 'Gallons')
        fuel_change = abs(fuel - last_fuel)
        if fuel_change > 0:
            fuelF = "{:.1f}".format(fuel)
            fuelF = fuelF + " Fuel"
            text.UpdateText("Line-2", fuelF)
            print("fuelF:", fuelF)
            last_fuel = fuel
            update = True
    except ValueError:
        print()

    try:
        hobbs = float(automationhat_bytes[9:14]) / 10
        print('Hobbs: ', '{0:6.1f}'.format(hobbs), ' Hours')
        hobbs_change = abs(hobbs - last_hobbs)
        if hobbs_change > 0:
            hobbsF = "{:.1f}".format(hobbs)
            if hobbs < 1000:  hobbsF = hobbsF + " TT"
            text.UpdateText("Line-1", hobbsF)
            print("hobbsF:", hobbsF)
            last_hobbs = hobbs
            update = True
    except ValueError:
        print()
    if update or loop_count > 50:
        text.WriteAll()
        update = False
        loop_count = 0
    loop_count += 1
    print()
#    sleep(60)
