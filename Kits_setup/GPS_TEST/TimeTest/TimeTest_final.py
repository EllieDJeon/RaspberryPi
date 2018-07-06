# Retrieve Sensor data
from sense_hat import SenseHat
sense = SenseHat()
sense.clear()

# Emergency Button data
from button import *

# GPS data
import serial
import pynmea2
gps = serial.Serial("/dev/ttyUSB0", baudrate = 9600, timeout=10000)

# Time
from datetime import datetime
from pytz import timezone
ts = "%Y-%m-%d %H:%M:%S"


'''-------------------------- Define functions --------------------------'''

def TimeStamp(timeZone = 'America/Chicago'):
	# return local time (default = Chicago)
        tzone = datetime.now(timezone(timeZone))
        dtime = tzone.strftime(ts)
        return dtime

def KeyInfo(camID='raspberry'):
	# define 'message' dict and assign 'trip_start' and 'camera_id'
	message = {}
        message['trip_start'] = TimeStamp()
        message['camera_id'] = camID
	return message

def ButtonData():
	# get the button value as True/False
        button = Button(25)
        button = Button(25, debounce=1.0)
        buttonPress = button.is_pressed()
        return buttonPress

def SensorData():
	# assign the sensor data (Gyroscope, Accelermeter,and Magnetometer) 
        pitch, roll, yaw = sense.get_orientation().values()
        ax, ay, az = sense.get_accelerometer_raw().values()
        mx, my, mz = sense.get_compass_raw().values()

        # sensor
        message['gx'] = pitch
        message['gy'] = roll
        message['gz'] = yaw

        message['ax'] = ax
        message['ay'] = ay
        message['az'] = az

        message['mx'] = mx
        message['my'] = my
        message['mz'] = mz
	return message

def GPSReader(line):
	# assign the GPS data
        if line.find('RMC') > 0:
                data = pynmea2.parse(line)
                message['time_stamp'] = data.timestamp
                message['speed'] = data.spd_over_grnd
                message['location'] = str(round(data.latitude,4)) + "," + str(round(data.longitude))
        if line.find('GGA') > 0:
                data = pynmea2.parse(line)
                message['altitude'] = data.altitude
                message['satellites'] = data.num_sats
                message['gps_qual'] = data.gps_qual
        if line.find('GSA') > 0:
                data = pynmea2.parse(line)
                #print('GPGSA_line : ', data) # check the gps data line
                message['hdop'] = data.hdop
        if line.find('GSV') > 0:
                data = pynmea2.parse(line)
                message['heading'] = data.azimuth_1
                #print('GPGSV_line : ', data) # check the gps data line
        return message

'''-------------------------- Save data --------------------------'''

# assign the starting distance values
preSpeed = 0.0
preTime = datetime.strptime(TimeStamp(), ts)
cumdistance = 0.0

# get the 'trip_start' time
tzone = datetime.now(timezone('America/Chicago'))
tripstart = tzone.strftime(ts)

basicInfo = KeyInfo('raspberry1') # save key information

line = gps.readline() # read the first gps line

publish = 1 # keep this way to apply to the AWS python file easily


# publish to the same topic in a loop forever
while True:

    gpsList = [] # save ALL sensor and gps data (default = 10 rows)
    if publish == 1:

	message = basicInfo.copy()

        # GPS
	# check if the line start with '$GPRMC'. This is the first line of the gps data.
        if line.find('RMC') is -1 : line = gps.readline()
        else:
                while True:
			print('first(GPS) : ', TimeStamp())
                        #line = gps.readline()
                        #if line.find('RMC') is -1 : line = gps.readline()
                        message.update(GPSReader(line)) # add gps data to message
                        line = gps.readline() # read next gps line
                        if len(message) == 8 : break # break if the message is full
                        #print(len(message), message)

		# Button
		message['emergencyCall'] = ButtonData()
		message.update(SensorData())
		print('second(button&sensor) : ', TimeStamp())

        	# append one message(row) to 'gpsList' and reset the 'data'
	        gpsList.append(message)

		message['time_stamp'] = TimeStamp()
		print('third(timestamp) : ', TimeStamp())

		# distance
		currTime = datetime.strptime(message['time_stamp'],ts)

                # check current speed
                if message['speed'] == None:
                        currSpeed = 0.0
                        distance = 0.0
#			print('NOT moving')
                else:
                        currSpeed = round(message['speed']*10/36,2) # conver into m/s
                        distance = (currSpeed - preSpeed)*((currTime - preTime).seconds)
#			print('moving')

		preTime = currTime
		preSpeed = currSpeed
		cumdistance += distance
		message['distance'] = round(cumdistance, 4)
		print('fourth(distance) : ', TimeStamp())
		#print(message)
		print('===================================================')
###################### save as local file #####################################
# save 'gpsList' as a local file (this json file has 10 rows)
		if len(gpsList) == 10:
			with open("GPS_DATA.json", mode='a') as f:
				json.dump(gpsList, f)
				#f.write("\n")
				gpsList = [] # reset 'gpsList'
###############################################################################

