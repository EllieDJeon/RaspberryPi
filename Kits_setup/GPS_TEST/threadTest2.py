# Retrieve Sensor data
from sense_hat import SenseHat
sense = SenseHat()
sense.clear()

# GPS data
import serial
import pynmea2
gps = serial.Serial("/dev/ttyUSB0", baudrate = 9600, timeout=10000)

# Time
from datetime import datetime
from pytz import timezone
ts = "%Y-%m-%d %H:%M:%S"

import json
import threading
import time
import queue

'''
sensor_gx = []
sensor_gy = []
sensor_gz = []       
sensor_ax = []
sensor_ay = []
sensor_az = []       
sensor_mx = []
sensor_my = []
sensor_mz = []
'''
msg['gx'], msg['gy'], msg['gz'], msg['ax'], msg['ay'], msg['az'], msg['mx'], msg['my'],msg['mz'] = ([] for i in range(9))
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


def SensorData(stopEvent, timeFinish, arg, q):
        '''
        global sensor_gx,sensor_gy, sensor_gz
        global sensor_ax, sensor_ay, sensor_az
        global sensor_mx, sensor_my, sensor_mz
        '''
        while not stopEvent.is_set():
                while time.time() < timeFinish:
                        # assign the sensor data (Gyroscope, Accelermeter,and Magnetometer) 
                        pitch, roll, yaw = sense.get_orientation().values()
                        ax, ay, az = sense.get_accelerometer_raw().values()
                        mx, my, mz = sense.get_compass_raw().values()
        
                        msg['gx'].append(pitch)
                        msg['gy'].append(roll)
                        msg['gz'].append(yaw)
                        msg['ax'].append(ax)
                        msg['ay'].append(ay)
                        msg['az'].append(az) 
                        msg['mx'].append(mx)
                        msg['my'].append(my)
                        msg['mz'].append(mz)
                        q.put(msg)
                        if stopEvent.is_set():
                                print("stop events accur: break 'sensor' ")
                                break
                        if time.time() > timeFinish:
                                print("time limit exceeded")
                                stopEvent.set()
                print("STOP: Stopping as you wish.")
                                
                
def GPSReader(line):
        # assign the GPS data
        if line.find('RMC') > 0:
                data = pynmea2.parse(line)
                message['time_stamp'] = data.timestamp
                message['speed'] = data.spd_over_grnd
                message['location'] = str(round(data.latitude,4)) + "," + str(round(data.long$
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


basicInfo = KeyInfo('raspberry1') # save key information
#tripstart = basicInfo['trip_start']
print('trip_start : ', tripstart)
line = gps.readline() # read the first gps line

publish = 1 # keep this way to apply to the AWS python file easily

gpsList = [] # save ALL sensor and gps data (default = 10 rows)

# publish to the same topic in a loop forever
while True:

    if publish == 1:

        message = basicInfo.copy()

        # GPS
        # check if the line start with '$GPRMC'. This is the first line of the gps data.
        if line.find('RMC') is -1 : line = gps.readline()
        else:
                #msg = {}
                stopEvent = threading.Event()
                timeFinish = time.time() + 99
                stopEvent.clear
                print('GPS start')
                while True:
                        q = queue.Queue()
                        t = threading.Thread(target=SensorData, args=(stopEvent, timeFinish, "sensor",q))
                        t.start()
                        t.result_queue = q 
                        message.update(GPSReader(line)) # add gps data to message
                        line = gps.readline() # read next gps line
                        if len(message) == 8 : 
                                print("setting stopEvent on gps")
                                stopEvent.set()
                                break # break if the message is full
                                
                # Button
                message['emergencyCall'] = ButtonData()
                message.update(SensorData())

                # append one message(row) to 'gpsList' and reset the 'data'
                gpsList.append(message)

                message['time_stamp'] = TimeStamp()
   
        
        
        
        

       
        
        
        
        
        
        
        
        
        
        
        
        
        
