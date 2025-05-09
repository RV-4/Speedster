#!/usr/bin/env python
#/home/pi/temp/smoke-ePaper.py

#					SMOKING Pi Zero   Version: 2.5.ePaper 0.7

# Python program to receive level of smoke oil tank
# from Automationhat Pi via OTG serial port
# and display level and possibly Total Time to an ePaper
# display from Papirus.

# To run at boot add the following to the END of /etc/rc.local

#			sudo python /home/pi/temp/smoke-ePaper.py &



# Input is from an Automation hat. 0-4 volts.


# V 1.0
# Recalibrated voltage to level reading.
# Added a deadband for level change before updating display.

# V 1.1
# Recalibrated again.
# Reduced sleep time.
# Changed booting text.

# V 2.0
# Added debug printing to counsel.
# Added Adafruit 128x32 OLED display (ePaper display broke).
# Calculate Gallons from voltage and display that.

# V 2.1
# Fixed weird identing.  ie. converted spaces to TABs.

# V 2.2
# Recalibration at .5 gallon marks really done in V 2.2 not 2.1

# V 2.3   (3/25/2018}
# Fixed syntax errors.

# V 2.3.1 (3/27)
# Version without OLED display.
# V 2.3.2 found more "disp.", ".draw", and "height" lines to comment out.

# V2.3.ePaper.1
# updated version standard
# .2 syntax error

# V2.3.ePaper.3
# Found more OLED code and reduced sleep time at the start 

# V2.3.ePaper.4
# Adjusted format of ePaper printout
# .5 changed voltage display to gallons

# V2.4 ePaper .6
# further cleanup to remove local Automationhat
# ePaper .7 (converted text to float)

print("PaPiRus ePaper Smoke.py")
print("Version 2.4.ePaper.7")

import time
import serial
from papirus import PapirusTextPos
import subprocess

# time.sleep(5.0)  # Papirus needs to wait for the pi to finish booting.


text = PapirusTextPos(False)

text.Clear()
time.sleep(1.0)
text.AddText("N221TM", 30 ,0, 39, Id="Line-1")
text.AddText("SMOKE TANK", 10, 36, 30, Id="Line-2")
text.AddText("BOOTING", 15, 60, 39, Id="Line-3")
#                    Start column, start row, height, Identification
text.WriteAll()

time.sleep(2.0)

# Define serial link to Automationhat via USB OTG cable
automationhat_serial = serial.Serial(
    port='/dev/ttyGS0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=None
)

automationhat_text = automationhat_serial.read_until(b'\r', None)
print("From Automationhat:", automationhat_text)
last_value = float(automationhat_text[0:3])
print("Last_Value:", last_value)
automationhat_text = automationhat_serial.read_until(b'\r', None)
print("From Automationhat:", automationhat_text)
value = float(automationhat_text[0:3])
print("Value:", value)

while True:
	# Write to PaPiRus display here
	gallons = (value - 0.216)/0.630
	if value   > 3.84: gallons = 5.5
	elif value > 3.30: gallons = 5.0
	elif value > 3.03: gallons = 4.5
	elif value > 2.74: gallons = 4.0
	elif value > 2.33: gallons = 3.5
	elif value > 1.90: gallons = 3.0
	elif value > 1.57: gallons = 2.5
	elif value > 1.24: gallons = 2.0
	elif value > 0.70: gallons = 1.5
	elif value > 0.25: gallons = 1.0
	elif value > 0.22: gallons = 0.5
	

	
#	print(gallons)
	gallonsF = "{:.1f}".format(gallons)
	gallonsF = gallonsF + " Gal"
	if value < 0.22: gallonsF = "-EMPTY-"
	text.UpdateText("Line-3", gallonsF)
	print("GallonsF:", gallonsF)
	Level2 = "{:.2f}".format(value)
	print("Level2:", Level2)
	Level3 = Level2 + " V"
	print ("Level3:", Level3)

#	value = .1
	if value > 3.20: Level = "--FULL--"
	if value < 3.21: Level = "  3/4"
	if value < 2.30: Level = "  1/2"
	if value < 1.40: Level = "  1/4"
	if value < 0.30: Level = "-EMPTY-"
	
##	if value > 3.20: gallonsF = "--FULL--"

	
	print ("Level:", Level)
##	text.UpdateText("Line-3", Level)
##	text.UpdateText("Line-1", Level3)

	text.WriteAll()
	change = abs(value - last_value)
	print("change:", change)
	while change < 0.05:
		automationhat_text = automationhat_serial.read_until(b'\r', None)
		value = float(automationhat_text[0:3])
		change = abs(value - last_value)
	print("change:", change)
	last_value = value

exit()
