#!/usr/bin/python3

#imports
import spidev
from time import sleep,strftime  # To add delay and display time
from array import *
from datetime import datetime, timedelta, time
import RPi.GPIO as GPIO
import atexit


#Define Variables
delay = 0.5
ldr_channel = 0

#Create SPI
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000 #setting the maximum frequency of the spi

#define input pins for the buttons:
RESET_SWITCH = 11 #button for reset the timer and cleaning the console
FREQUENCY_CHANGE_SWITCH =15 #button to be used to change the frequency of the application
STOP_START_SWITCH = 29 #the button to be used to start and stop the taking of data
DISPLAY_SWITCH = 33 #button to display the results

#variables to be used in the program
frequency = .5
readings_recorded = [None]*5
timer = 0
recording = True
index =0

def exit_handler():
    print("Cleaning up")
    GPIO.cleanup()

atexit.register(exit_handler)

def format_time(t):
    tm = timedelta(seconds = t)
    datet = datetime(1,1,1) + tm
    hr =  str(datet.hour) if datet.hour > 9 else '0' + str(datet.hour)
    min = str(datet.minute) if datet.minute > 9 else '0' + str(datet.minute)
    sec = str(datet.second) if datet.second >9 else '0' + str(datet.second)
    return hr+":"+min+":"+sec

def output(readings):
   deg =u'\xb0'
   print("_________________________________________________________")
   print("Time     Timer    Pot   Temp Light")
   for i in range(0, 5):
       if readings[i]is not None:
            print("{} {} {}V {}C {}%".format(readings[i][0], readings[i][1], readings[i][2], str(readings[i][3])+deg, readings[i][4]))
            print("_________________________________________________________")
	  
def delay():
    sleep(2)

def display_handler(channel_number): #pin number is the pin that caused this event
    print("Display pressed\n")
    global readings_recorded
    output(readings_recorded)
 
 
def freq_change_handler(channel_number):
    global frequency
    print("Change frequency presse")
    if frequency == .5:
        frequency = 1
    elif frequency == 1:
        frequency = 2
    elif frequency == 2:
        frequency = .5
   

def reset_handler(channel_number):
    print("\033[H\033[J")
    print("reset pressed")
   

def start_stop_handler(channel_number):
    global recording
    print("Stop/Start pressed")
    recording = True if (recording == False) else False

#setting board and gpio pins
GPIO.setmode(GPIO.BOARD)
GPIO.setup(RESET_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(FREQUENCY_CHANGE_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(STOP_START_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(DISPLAY_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#setting up event listenrs for the three buttons
GPIO.add_event_detect(RESET_SWITCH,GPIO.RISING,callback=reset_handler, bouncetime=300)
GPIO.add_event_detect(FREQUENCY_CHANGE_SWITCH,GPIO.RISING, callback=freq_change_handler, bouncetime=300)
GPIO.add_event_detect(STOP_START_SWITCH, GPIO.RISING, callback = start_stop_handler, bouncetime=300)
GPIO.add_event_detect(DISPLAY_SWITCH, GPIO.RISING, callback = display_handler, bouncetime=300)


def readadc(adcnum):
    # read SPI data from the MCP3008, 8 channels in total
    if adcnum > 7 or adcnum < 0:
        return -1
    r = spi.xfer2([1, 8 + adcnum << 4, 0])
    data = ((r[1] & 3) << 8) + r[2]
    return data

# Below function will convert data to voltage
def convert_volts(data):
	volts = (data * 3.3) / float(1023)
	volts = round(volts, 2) # Round off to 2 decimal places
	return volts
def get_time():
	return strftime("%H:%M:%S")
	
# Below function will convert data to temperature.
def convert_temp(data):
	temp = ((data * 330)/float(1023))-50
	temp = round(temp)
	return temp

def record_readings():   
    global timer
    global readings
    global frequency
    global index

    if recording:
       current_time =  get_time()
       ldr_reading = int(100-(readadc(0)/1024)*100)
       temp_reading = convert_temp(readadc(1))
       pot_reading = convert_volts(readadc(2))
       t = format_time(timer)
       recordings = [current_time, t, pot_reading, temp_reading, ldr_reading]
       readings_recorded.remove(readings_recorded[0])
       readings_recorded.append(recordings)
#	   index = (index+1)%5
    timer += frequency 

def main():
    global frequency
    global readings_recorded
    while True:
        ldr_value = readadc(ldr_channel)
        if recording:
            output(readings_recorded)
        sleep(frequency)
        record_readings()

if __name__ == "__main__": main()
