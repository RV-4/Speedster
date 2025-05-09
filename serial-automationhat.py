#!/usr/bin/env python
# run on main pi with Automationhat hat called "1TM-Pi"

# /home/pi/1TM/serial-automationhat.py

#  Version 1.5.2 testing
print("serial-automationhat.py Version 1.5.2.Testing")

# TODO Add error handling for opening serial ports
# FileNotFoundError: [Errno 2] No such file or directory: '/dev/ttyUSB0'

# TODO Add "Hello World" serial transmission to PaPiRus Pi to signal Comms OK
# TODO Add IP address and Gateway address and send to PaPiRus display

# Raspberry Pi 3 with AutomationHat.
# /dev/ttyUSB0 is a USB to RS-232 converter to receive data from
# the Dynon HDX via Serial out.
# /dev/ttyACM0 is a micro-USB cable plugged into a Pi-Zero OTG port
#                 /dev/ttyAMA0 for Pi-4

# To check serial ports use:   dmesg | grep tty
# To check I2C devices:        sudo i2cdetect -y 0
# To check MQTT status:        sudo systemctl status mosquitto

# To install and setup the MQTT Broker:
#  sudo apt install mosquitto mosquitto-clients
#  sudo systemctl enable mosquitto

# To install MQTT library in Python
#   sudo pip3 install paho-mqtt

# To install automation hat run:
#     curl https://get.pimoroni.com/automationhat | bash

# To run at boot must have entry in /etc/rc.local
# sudo python3 /home/pi/1TM/serial-automationhat.py &

# Write Serial data to PaPiRus Pi
# Format of data stream is:
# !41+ssssGhhhhhfff
# "+ssssG"   is the amount of smoke oil remaining in tenths of gallons
# "hhhhh"    is the Total Time (Hobbs Time) in tenths of hours from Dynon EMS
# "fff"      is the Total Fuel Remaining in tents of gallons

import serial
from time import sleep
import paho.mqtt.client as mqtt #import the client
import sys
import os
import socket

print("Waiting 20 seconds to ensure Pi is fully booted")
sleep(20)  # Wait for bootup to complete

############  For receiving mqtt messages
def on_connect_cloud(client, userdata, flags, rc):
    print("Connected to cloud mosquito broker with result code " + str(rc))
    client_cloud.subscribe("1TM")

def on_connect_lcl(client, userdata, flags, rc):
    print("Connected to local mosquito broker with result code " + str(rc))
    client_lcl.subscribe("1TM")

def on_message(client, userdata, message):
    nothing = 0                             # do nothing to save time
    print("message received: " ,str(message.payload.decode("utf-8")))
#    print("message topic=",message.topic)
#    print("message qos=",message.qos)
#    print("message retain flag=",message.retain)

def on_disconnect_lcl(client, userdata, rc):
    if rc != 0:
        print(client, " Unexpected disconnection from local mosquito broker.")

def on_disconnect_cloud(client, userdata, rc):
    if rc != 0:
        print(client, " Unexpected disconnection from cloud mosquito broker.")

########################################
broker_address_lcl   = "localhost"
broker_address_cloud = "broker.mqtt.cool"
#broker_address = "iot.eclipse.org"
print("creating new MQTT Client instances")

client_cloud = mqtt.Client() #create new instance
client_cloud.on_message = on_message #attach function to callback
client_cloud.on_connect = on_connect_cloud
client_cloud.connect(broker_address_cloud, 1883, 60)
client_cloud.loop_start() #start the loop
client_cloud.on_disconnect = on_disconnect_cloud

client_lcl = mqtt.Client()
client_lcl.on_message = on_message #attach function to callback
client_lcl.connect(broker_address_lcl,  1883, 60)
client_lcl.loop_start() #start the loop
client_lcl.on_connect = on_connect_lcl
client_lcl.on_disconnect = on_disconnect_lcl

print()
sleep(2)

client_lcl.publish("1TM", "Message from serial-automationhat.py to Local Host")
client_cloud.publish("1TM", "Message from serial-automationhat.py to the Cloud")

#########################################


sleep(2)       # Wait for the USB ports to activate

# Define serial link to Dynon HDX via RS-232 USB Adapter
dynon_serial = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

# Define serial link to PaPaRus display Pi via OTG cable to PiZero
papirus_serial = serial.Serial(
    baudrate=9600,
    port=  '/dev/ttyACM0',
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    writeTimeout=0
)

hobbs           = 0   # Initialize hobbs meter as 0 (don't I wish...)
smoke           = 0   # Initialize smoke oil tank as empty
flap_position   = 0   # Initialize flaps as up
old_IAS         = 1.1
old_fuel_remain = 1.1
old_smoke       = 1.1
old_hobbs       = 1
old_flap_pos    = 1
update          = False
tx_count        = 0
loop_count     = 0     # print only max_print loops of debug messages
max_print       = 10

print("Welcome to N221TM's Raspberry Pi", sep=' ', end='\n\n\n')
print("Starting loop to read data from Dynon HDX:")
print()

dynon_serial.flushInput()                             # Assume starting in mid stream so clear out the buffer
dynon_bytes = dynon_serial.read_until(b'\r\n', None)  # Input from HDX will be a byte stream

try:
    gw = os.popen("ip -4 route show default").read().split()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((gw[2], 0))
    ipaddr = s.getsockname()[0]
    gateway = gw[2]
    host = socket.gethostname()
    print ("IP:", ipaddr, " GW:", gateway, " Host:", host)
except:
    print("Error: Unable to get IP address")

pub = "Host, " + host + "  IP Address, " + ipaddr
client_cloud.publish("1TM", pub)
client_lcl.publish("1TM", pub)

#  Send one dummy message to PaPiRus display pi to signal that comms are OK
#  and to test the serial link
papirus_str = "!41" + "+0231G" + "13590" + "312" + '\r\n'
papirus_bytes = papirus_str.encode()
try:
    papirus_serial.write(papirus_bytes)         # Send data to PaPiRus
except Exception as e:
    print(e)
    print("Unexpected error in write to PaPiRus: ", e)
print("To  Papirus:", papirus_str)

while True:
    tx_count = tx_count + 1
    dynon_bytes = dynon_serial.read_until(b'\r\n', None)   # Input from HDX will be a byte stream
    if loop_count < max_print:  print('dynon_bytes: ', dynon_bytes)
    try:
        dynon_str = dynon_bytes.decode("ascii")
    except ValueError:
        print("must have received non ascii trash")
    # Dynon uses ASCII encoding not utf-8.

#    print('Input test string from Dynon:')                  # For Testing take input from console
#    dynon_str = input()

#    print(dynon_str)
#    print()

    if dynon_str.startswith('!1'):                          # Dynon Skyview ADAHRS  Data
        if dynon_str[23:27].isnumeric():
            IAS = float(dynon_str[23:27]) /10
            if old_IAS != IAS:                              # Speed changed
                if loop_count < max_print:  print('IAS:         {0:5.1f}'.format(IAS), 'kts')
                pub = "IAS," + dynon_str[23:27]
                client_cloud.publish("1TM", pub)                      # Send to the mqtt cloud
                client_lcl.publish("1TM", pub)                  # Send to the local mqtt broker
                old_IAS = IAS
                update = True
        else: print('Trash for ,IAS:', dynon_str[23:27])
    elif dynon_str.startswith('!2'):                          # Dynon Skyview NAV/Autopilot Data
        pass
    elif dynon_str.startswith('!3'):                        # Dynon Skkyview EMS  Data
        if dynon_str[44:47].isnumeric():
            fuel_remain = float(dynon_str[44:47]) / 10
            if old_fuel_remain != fuel_remain:
                if loop_count < max_print:  print('Fuel Remaining:', '{0:4.1f}' .format(fuel_remain))
                pub = "Fuel," + dynon_str[44:47]
                client_cloud.publish("1TM", pub)
                client_lcl.publish("1TM", pub)
                old_fuel_remain = fuel_remain
                update = True
        if dynon_str[142:146].isnumeric():
            smoke = float(dynon_str[142:146]) /10
            if old_smoke != smoke:
                if loop_count < max_print:  print('Smoke Level:     {0:3.1f}'.format(smoke), 'Gallons')
                pub = "Smoke," + dynon_str[142:146]
                client_cloud.publish("1TM", pub)
                client_lcl.publish("1TM", pub)
                old_smoke = smoke
                update = True
        else: print('Trash for Smoke Level:', dynon_str[141:147])  # Includes "+" and "G"
        if dynon_str[154:158].isnumeric():
            pub = "Flaps," + dynon_str[154:158]
            client_lcl.publish("1TM", pub)
            if old_flap_pos != flap_position:
                flap_position = int(dynon_str[154:158])
                if loop_count < max_print:
                    print('Flaps at:       ', ' {0:,}'.format(flap_position), 'Degrees Down', sep=' ', end='\n\n\n')
                client_cloud.publish("1TM", pub)
                old_flap_pos = flap_position
                update = True
        else:  print('Flaps:         ', dynon_str[153:158])
        if dynon_str[57:62].isnumeric():
            hobbs = float(dynon_str[57:62]) /10
            if old_hobbs != hobbs:
                if loop_count < max_print:  print('Hobbs:         {0:6.1f}' .format(hobbs), 'Hours')
                pub= "Hobbs," +  dynon_str[57:62]
                client_cloud.publish("1TM", pub)
                client_lcl.publish("1TM", pub)
                old_hobbs = hobbs
                update = True
        else: print('Trash for Hobbs:', dynon_str[57:62])
        if loop_count < max_print:  print()



#  ##############################################################
#        client.will_set("1TM", "Disconnected without calling disconnect")
#        client_cloud.on_disconnect = on_disconnect
#        client_cloud.loop_start() #start the loop
#        time.sleep(1)      # wait
#        client_cloud.loop_stop()  #stop the loop

#        client_lcl.on_disconnect = on_disconnect
#        client_lcl.loop_start() #start the loop
#        time.sleep(1)      # wait
#        client_lcl.loop_stop()  #stop the loop

#	##############################################################

    else:
        print('Unexpected data from Dynon:', dynon_str, sep=' ', end='\n\n\n')
        update = False

# Build text string to send to PaPiRus display pi
    if update or tx_count > 10:
        smoke_str = dynon_str[141:147]      #   "+nnnnG"
        hobbs_str = dynon_str[57:62]
        fuel_remain_str = dynon_str[44:47]
        papirus_str = '!41' + smoke_str + hobbs_str + fuel_remain_str + '\r\n'
        if loop_count < max_print:  print("To  Papirus:", papirus_str)
        papirus_bytes = papirus_str.encode()
        print(papirus_bytes)
        try:
            papirus_serial.write(papirus_bytes)         # Send data to PaPiRus
        except Exception as e:
            print(e)
            print("Unexpected error in write to PaPiRus: ", e)
#               pass
        update = False
        tx_count = 0

    loop_count = loop_count + 1

client_lcl.loop_stop()    #stop the loop
client_cloud.loop_stop()  #stop the loop
#    sleep(1)



