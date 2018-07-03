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

# time
from datetime import datetime
from pytz import timezone
ts = "%Y-%m-%d %H:%M:%S"


def TimeStamp(timeZone = 'America/Chicago'):
        tzone = datetime.now(timezone(timeZone))
        dtime = tzone.strftime(ts)
        #message['time_stamp'] = dtime
        return dtime

def loca_format(coord):
	# DDDMM.MMMMM -> DD.MMMM
	# "location":"41.8923,-87.6155"
	if coord == 0.0 or coord is ' ': return 0.0
	else:
		v = coord.split(".")
		head = v[0]
		tail =  v[1]
		deg = head[0:-2]
		minu = head[-2:]
		if len(deg) == 3 : reform = "-" + deg[1:] + "." + minu + tail
		else: reform = deg + "." + minu + tail
		return str(round(float(reform), 4))

'''Test function:
lat = '4142.86751'
longi = '08803.24426'

loca_format(lat) + "," + loca_format(longi)
'''
def KeyInfo(camID='raspberry'):
	message = {}
        message['trip_start'] = TimeStamp()
        message['camera_id'] = camID
	return message

def ButtonData():
        button = Button(25)
        button = Button(25, debounce=1.0)
        buttonPress = button.is_pressed()
        return buttonPress

def SensorData():
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

        if line.find('RMC') > 0:
                data = pynmea2.parse(line)
                message['time_stamp'] = data.timestamp
                message['speed'] = data.spd_over_grnd
                #message['location'] = loca_format(data.lat) + "," + loca_format(data.lon)
                message['location'] = str(data.latitude) + "," + str(data.longitude)
        if line.find('GGA') > 0:
                data = pynmea2.parse(line)
                message['altitude'] = data.altitude
                message['satellites'] = data.num_sats
                message['gps_qual'] = data.gps_qual
        if line.find('GSA') > 0:
                data = pynmea2.parse(line)
                #print('GSA_hdop : ', data)
                message['hdop'] = data.hdop
        if line.find('GSV') > 0:
                data = pynmea2.parse(line)
                message['heading'] = data.azimuth_1
                #print('GSV_heading : ', data)
        return message

'''start distance'''
preSpeed = 0.0
preTime = TimeStamp()
cumdistance = 0.0

line = gps.readline() # read the first gps line

repeat = 1

# Publish to the same topic in a loop forever
while True:

    gpsList = [] # save ALL sensor and gps data (10 rows)
    if repeat == 1:

#        tzone = datetime.now(timezone('America/Chicago'))
#        dtime = tzone.strftime(ts)
#	message = {}
#        message['trip_start'] = dtime
#	message['camera_id'] = 'raspberry'

	message = KeyInfo('raspberry1')

        # Button
#	message['emergencyCall'] = ButtonData()

        # GPS
	# check if the line start with '$GPRMC'. This is the first line of the gps data.
        if line.find('RMC') is -1 : line = gps.readline()
        else:
		i=0
                while True:
			#print(i, 'line')
                        #line = gps.readline()
                        #if line.find('RMC') is -1 : line = gps.readline()
                        message.update(GPSReader(line)) # add gps data to message
                        line = gps.readline() # read next gps line
			i += 1
                        if len(message) == 8 : break # break if the message is full
                        #print(len(message), message)

#	message.update(KeyInfo('raspberry1'))
		# Button
		message['emergencyCall'] = ButtonData()
		message.update(SensorData())

        	# append one message(row) to 'gpsList' and reset the 'data'
	        gpsList.append(message)
		#print(message)

		message['time_stamp'] = TimeStamp()
		#print('EndTime: ', endTime, message)

		currTime = datetime.strptime(message['time_stamp'],ts)

                # current speed
                if message['speed'] == None:
                        currSpeed = 0.0
                        distance = 0.0
                else:
                        currSpeed = message['speed']*(10/36) # message['speed'], conver into m/s
                        distance = (currSpeed - preSpeed)*(currTime - preTime)

#                print(preSpeed, preTime, currSpeed, currTime)

		preTime = currTime
		preSpeed = currSpeed
		cumdistance += distance
		message['distance'] = cumdistance
		print(message)

###################### save as local file #####################################
# save 'gpsList' as a local file (this json file has 10 rows)
	if len(gpsList) == 10:
		with open("GPS_DATA.txt", mode='a') as f:
			json.dump(gpsList, f)
			#f.write("\n")
			gpsList = [] # reset 'gpsList'
###############################################################################

