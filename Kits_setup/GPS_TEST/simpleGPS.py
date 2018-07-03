

# time
from datetime import datetime 
from pytz import timezone
ts = "%Y-%m-%d %H:%M:%S"

# GPS data
import serial
import pynmea2
gps = serial.Serial("/dev/ttyUSB0", baudrate = 9600, timeout=10000)


def TimeStamp(timeZone = 'America/Chicago'):
        tzone = datetime.now(timezone(timeZone))
        dtime = tzone.strftime(ts)
        #message['time_stamp'] = dtime
        return dtime

def GPSReader(line):
	
	if line.find('RMC') > 0:
		data = pynmea2.parse(line)
		message['time_GPS'] = data.timestamp
		message['speed'] = data.spd_over_grnd
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

def Distance(preSpeed, preTime, currSpeed, currTime):
	if currSpeed == None: distance = 0.0
	else:
		distance = (currSpeed - preSpeed)*(currTime - preTime)
		preTime = currTime
		preSpeed = currSpeed
	return distance





line = gps.readline() # read the first gps line

'''start distance'''
preSpeed = 0.0
preTime = TimeStamp()
cumdistance = 0.0


while True:
	message = {}

	# check if the line start with '$GPRMC'. This is the first line of the gps data.
	if line.find('RMC') is -1 : line = gps.readline()
	else:
		while True:
			message.update(GPSReader(line)) # add gps data to message
			line = gps.readline() # read next gps line
			if len(message) == 8 : break # break if the message is full
			#print(len(message), message)

		#currSpeed = message['speed']*(10/36) # message['speed'], conver into m/s
	       #currTime = message['time_stamp'].total_second() # message['time_stamp'
		message['time_stamp'] = TimeStamp()
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
