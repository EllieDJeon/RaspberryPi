'''
/*
 * Copyright 2010-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import json
import jsonschema
from jsonschema import validate
import yaml


AllowedActions = ['both', 'publish', 'subscribe']

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")

# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                    help="Use MQTT over WebSocket")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicPubSub",
                    help="Targeted client id")
parser.add_argument("-t", "--topic", action="store", dest="topic", default="sdk/test/Python", help="Targeted topic")
parser.add_argument("-m", "--mode", action="store", dest="mode", default="both",
                    help="Operation modes: %s"%str(AllowedActions))
parser.add_argument("-M", "--message", action="store", dest="message", default="Hello World!",
                    help="Message to publish")

parser.add_argument("-A", "--accelerometer", action="store_true", default=False)
parser.add_argument('-G','--gyroscope', action='store_true', default=False)
parser.add_argument('-Ma','--magnetometer', action='store_true', default=False)

parser.add_argument("-P", "--airpressure", action="store_true", default=False)
parser.add_argument("-T", "--temperature", action="store_true", default=False)
parser.add_argument('-H','--humidity', action='store_true', default=False)

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
useWebsocket = args.useWebsocket
clientId = args.clientId
topic = args.topic

if args.mode not in AllowedActions:
    parser.error("Unknown --mode option %s. Must be one of %s" % (args.mode, str(AllowedActions)))
    exit(2)

if args.useWebsocket and args.certificatePath and args.privateKeyPath:
    parser.error("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
    exit(2)

if not args.useWebsocket and (not args.certificatePath or not args.privateKeyPath):
    parser.error("Missing credentials for authentication.")
    exit(2)

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
if useWebsocket:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId, useWebsocket=True)
    myAWSIoTMQTTClient.configureEndpoint(host, 443)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath)
else:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
    myAWSIoTMQTTClient.configureEndpoint(host, 8883)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
if args.mode == 'both' or args.mode == 'subscribe':
    myAWSIoTMQTTClient.subscribe(topic, 1, customCallback)
time.sleep(2)


# Retrieve Sensor data
from sense_hat import SenseHat
sense = SenseHat()
sense.clear()

# Emergency Button data
from button import *

# GPS data
import serial, pynmea2
gps = serial.Serial("/dev/ttyUSB0", baudrate = 9600, timeout=10000)

# time
from datetime import datetime
from pytz import timezone
ts = "%Y-%m-%d %H:%M:%S"

import threading, time, json, csv
from Queue import Queue

# geofence
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


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
	message['event'] = ' '
        return message

def ButtonData():
        # get the button value as True/False
        button = Button(25)
        button = Button(25, debounce=1.0)
        buttonPress = button.is_pressed()
        return buttonPress

def SensorData(stopEvent, timeFinish, q):
        global msg # collect the sensor data
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
                                break
                        if time.time() > timeFinish:
                                stopEvent.set()
                                #print("STOP: Stopping as you wish.")

def GeoFence(location, zone):
	polygon = Polygon(zone)
	lat = float(location.split(',')[0])
	long = float(location.split(',')[1])
	point = polygon.contains(Point(lat, long))
	return point

def GPSReader(line):
        # assign the GPS data
        if line.find('RMC') > 0:
                data = pynmea2.parse(line)
                message['time_stamp'] = data.timestamp
                message['speed'] = data.spd_over_grnd
#		message['1lat'] = loca_format(data.lat)
#		message['1long'] = data.lon
		message['aa_NEW_location'] = loca_format(data.lat) + "," + loca_format(data.lon)
                message['aa_location'] = str(round(data.latitude,4)) + "," + str(round(data.longitude))
		#message['geofence'] = GeoFence(data.latitude, data.longitude, zone) 
        if line.find('GGA') > 0:
                data = pynmea2.parse(line)
               # message['altitude'] = data.altitude
                message['a6_satellites'] = data.num_sats
                #message['gps_qual'] = data.gps_qual
        if line.find('GSA') > 0:
                data = pynmea2.parse(line)
                #print('GPGSA_line : ', data) # check the gps data line
                message['hdop'] = data.hdop
        if line.find('GSV') > 0:
                data = pynmea2.parse(line)
                message['heading'] = data.azimuth_1
                #print('GPGSV_line : ', data) # check the gps data line
        return message

def JsonSchema(message, schema):
	try: validate(message, schema)
	except jsonschema.exceptions.ValidationError as ve:
		print("Schema ERROR: ", ve)

def loca_format(coord):
	# DDDMM.MMMMM -> DD.MMMM
	# "location":"41.8923,-87.6155"
	if coord == 0.0 or coord is "": return '0.0'
	else:
		v = coord.split(".")
		head = v[0]
		tail =  v[1]
		deg = head[0:-2]
		minu = head[-2:]
		if len(deg) == 3 : reform = "-" + deg[1:] + "." + minu + tail
		else: reform = deg + "." + minu + tail
		return str(round(float(reform), 4))


'''-------------------------- Save data --------------------------'''

# read jsonschema file
schema_file = open('jsonschema_Rpi.json').read()
schema = yaml.load(schema_file)

# assign the starting distance values
preSpeed = 0.0
preTime = datetime.strptime(TimeStamp(), ts)
cumdistance = 0.0

basicInfo = KeyInfo('raspberry1') # save key information
tripstart = basicInfo['trip_start']
message = basicInfo.copy()
message['event'] = 'CarVi activated'
print('trip_start : ', tripstart)

# upload data to 'S3'
messageJson = json.dumps([message])

myAWSIoTMQTTClient.publish(topic, messageJson, 1)
if args.mode == 'publish':
	print('Published topic %s: %s\n' % (topic, messageJson))





line = gps.readline() # read the first gps line

gpsList = [] # save ALL sensor and gps data (default = 10 rows)

# geofence
zone1 = [(41.894711, -87.624239),(41.890000,-87.624113),(41.889985,-87.615144),(41.895011,-87.61652)]
zone2 = [(41.902326,-87.625044),(41.900614,-87.620992),(41.900859,-87.618637),(41.902367,-87.621320)]
#zone = [(40.0000, -87.0000), (40.0000, -89.0000), (42.0000, -87.0000), (42.0000, -89.0000)]
zone = [(-0.0001, 0.0001),(0.0001,0.0001), (0.0001,-0.0001),(-0.0001,-0.0001)]

# Publish to the same topic in a loop forever
while True:
	
    if args.mode == 'both' or args.mode == 'publish':
        
        message = basicInfo.copy()
#	message['event'] = 'normal' 

	print(message['event'])
        # GPS
        # check if the line start with '$GPRMC'. This is the first line of the gps data.
        if line.find('RMC') is -1 : line = gps.readline()
        else:
                msg = {}
                msg['gx'], msg['gy'], msg['gz'], msg['ax'], msg['ay'], msg['az'], msg['mx'], msg['my'],msg['mz'] = ([] for i in range(9)) 


                stopEvent = threading.Event()
                timeFinish = time.time() + 50
                stopEvent.clear
                while True:
                        q = Queue()
                        t = threading.Thread(target=SensorData, args=(stopEvent, timeFinish,q))
                        t.start()
                        t.result_queue = q
                        message.update(GPSReader(line)) # add gps data to message
                        line = gps.readline() # read next gps line
                        if len(message) == 8 :
                                stopEvent.set()
                                message.update(msg)
                                break # break if the message is full

		# GeoFence
		message['aaN_geo'] = GeoFence(message['aa_NEW_location'], zone)
		message['abN_geo'] = GeoFence(message['aa_NEW_location'], zone1)
		message['acN_geo'] = GeoFence(message['aa_NEW_location'], zone2)
                message['aa_geo'] = GeoFence(message['aa_location'], zone)
                message['ab_geo'] = GeoFence(message['aa_location'], zone1)
                message['ac_geo'] = GeoFence(message['aa_location'], zone2)



                # Button
                message['emergencyCall'] = ButtonData()

                # append one message(row) to 'gpsList' and reset the 'data'
                gpsList.append(message)

                message['time_stamp'] = TimeStamp()

                # distance
                currTime = datetime.strptime(message['time_stamp'],ts)

                # check current speed
                if message['speed'] == None:
                        currSpeed = 0.0
                        distance = 0.0
                else:
                        currSpeed = round(message['speed']*10/36,2) # conver into m/s
                        distance = currSpeed*((currTime - preTime).seconds)

                preTime = currTime
                #preSpeed = currSpeed
                cumdistance += distance
                message['distance'] = round(cumdistance, 4)
                #print(message['location'], message['geofence'])
                gpsList.append(message)
		
		# check schema
		JsonSchema(message, schema)

		# upload data to 'S3'
#		messageJson = json.dumps(message)
		messageJson = json.dumps(message)

		myAWSIoTMQTTClient.publish(topic, messageJson, 1)
		if args.mode == 'publish':
			print('Published topic %s: %s\n' % (topic, messageJson))


                ###################### save as local file #####################################
                # save 'gpsList' as a local file (this json file has 10 rows)
                if len(gpsList) == 10:
                        try:
                                print('Dumping')
                                with open("GPS_DATA_{}.txt".format(tripstart), mode='a+') as f:
                                        
					json.dump(gpsList, f)
					#f.write(gpsList)
					json.dump(',', f)
                                gpsList = [] # reset 'gpsList'
                        except: print('')
		#f.close()
                ###############################################################################

