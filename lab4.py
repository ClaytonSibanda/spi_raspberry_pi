#!/usr/bin/python
# Importing modules
import spidev # To communicate with SPI devices
from time import sleep,strftime  # To add delay and display time
# Start SPI connection
spi = spidev.SpiDev() # Created an object
spi.open(0,0) 
spi.max_speed_hz=1000000
#setup gpio

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
reset_button =40
stop_button=38
frequency_button =37
display_button=36

#set up falling edge detection for all the buttons
GPIO.setup(reset_button,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(stop_button,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(frequency_button,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(display_button,GPIO.IN,pull_up_down=GPIO.PUD_UP)

def reset(channel):
	print("reset button pressed")
def stop(channel):
	print("stop button pressed")
def changeFrequency(channel):
	print("freq change pressed")
def display(channel):
	print("display pressed")

GPIO.add_event_detect(reset_button,GPIO.FALLING,callback=reset,bouncetime=300)
#bouncetime sets a time during which time a second button press will be ignored
GPIO.add_event_detect(stop_button,GPIO.FALLING,callback=reset,bouncetime=300)
GPIO.add_event_detect(frequency_button,GPIO.FALLING,callback=reset,bouncetime=300)
GPIO.add_event_detect(display_button,GPIO.FALLING,callback=reset,bouncetime=300)



# Read MCP3008 data
def analog_input(channel):
	adc = spi.xfer2([1,(8+channel)<<4,0])
	data = ((adc[1]&3) << 8) + adc[2]
	return data
# Below function will convert data to voltage
def convert_volts(data):
	volts = (data * 3.3) / float(1023)
	volts = round(volts, 2) # Round off to 2 decimal places
	return volts
 
# Below function will convert data to temperature.
def convert_temp(data):
	temp = ((data * 330)/float(1023))-50
	temp = round(temp)
	return temp

def get_time():
	return strftime("%H:%M:%S")

print("_______________________________________________________")
print("Time   Timer   Pot  Temp   Light")
while True:
	temp_output = analog_input(0) # Reading from CH1
	temp       = convert_temp(temp_output)
	pot_output= analog_input(1)
	pot_volts = convert_volts(pot_output)
	print("_______________________________________________________")
	print(" {} {} V {} deg C".format(get_time(),pot_volts,temp))
	print("_______________________________________________________")
	sleep(0.5)
GPIO.cleanup() # release pins from this operation
