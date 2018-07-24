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
import yaml, os, boto3, glob, ast
import signal, sys

AllowedActions = ['both', 'publish', 'subscribe']

# Custom MQTT message callback
def customCallback(client, userdata, message):
    ''' Subscribe default topic '''
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")

def videoCallback(client, userdata, message):
    ''' Subscribe video topic '''
    videotopic = "sdk/test/request"
    print("from topic: ")
    print(videotopic)
    print("--------------\n\n")

    # create subscribe message to dictionary
    requestmsg = ast.literal_eval(message.payload)

    # 'message : get list' - upload the video list
    ''' message can be any topic that includes word 'list' '''
    if requestmsg["message"].find("list") >= 0:
        print("Video list requested")
        getVideoList(videotopic)

    # 'message : upload' - upload requested video file
    ''' message can be any topic that includes word 'upload' 
    videofile can be the last parts of the video file name '''
    if requestmsg["message"].find("upload") >= 0:
        print("Video uploading")
        videoFile = requestmsg["videofile"] # get the video file name
        uploadVideo(videotopic, videoFile)

# subscribe multiple topics
def listener():
    if args.mode == 'both' or args.mode == 'subscribe':
        myAWSIoTMQTTClient.subscribe("sdk/test/request", 1, videoCallback) # video request
        myAWSIoTMQTTClient.subscribe(topic, 1, customCallback) # default


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
parser.add_argument("-cr", "--camerarecord", action="store", dest="camerarecord", default='F', help="Camera recording")


# S3 parameters
parser.add_argument("-K", "--keyID", action="store", dest="accessKeyID", default="AKIAICFM4F6PFMZG4JKQ", help="Your AWS access key")
parser.add_argument("-S", "--secretkey", action="store", dest="accessSecretKey", default="MTf/tQtqKl6BFiC7XcVCPWqBEZqy/yhKYuD4mjMJ", help="Your AWS secret access key")
parser.add_argument("-B", "--bucket", action="store", default='raspberry22-backup', dest="bucketName", help="AWS bucket name")

args = parser.parse_args()
AWS_ACCESS = args.accessKeyID
AWS_SECRET = args.accessSecretKey
bucketName = args.bucketName

host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
useWebsocket = args.useWebsocket
clientId = args.clientId
topic = args.topic
camerarecord = args.camerarecord

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
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(30)  # 30 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
listener()

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
cts = "%Y%m%d_%H%M%S"

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
		message['location'] = LocaFormat(data.lat) + "," + LocaFormat(data.lon)
        if line.find('GGA') > 0:
                data = pynmea2.parse(line)
                message['satellites'] = data.num_sats
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

def LocaFormat(coord):
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

def CameraVideo(cdtime):
        os.system("avconv -f video4linux2 -r 10 -s 1280x960 -i /dev/video0 /home/pi/aws-iot-device-sdk-python/samples/basicPubSub/Camera/Rpi_video_{}.avi".format(cdtime))
        print("Camera recording start")

def PoweroffEvent(signal, frame):
	print("Ctrl+C received: Power Off")
	global basicInfo
	message = basicInfo.copy()
	message['event'] = "Power Off"
	print(message)

	# upload 'Power Off' message to 'S3'
	messageJson = json.dumps([message])
	myAWSIoTMQTTClient.publish(topic, messageJson, 1)
	if args.mode == 'publish':
		print('Published topic %s: %s\n' % (topic, messageJson))

	time.sleep(1)
	sys.exit(0)

def getVideoList(videotopic):
	print("Uploading list")
	session = boto3.Session(aws_access_key_id = AWS_ACCESS ,aws_secret_access_key = AWS_SECRET)
	client = session.client('s3')

	directory = os.popen('pwd').read().rstrip() + '/Camera' + '/'
	filelists = [os.path.basename(x) for x in glob.glob(str(directory) + '*.avi')]
	filename = "RPiVideoList.txt"
	file = open(directory + filename, "wb")
	for f in filelists:
		file.write(f + ',')
	file.close()

	# upload the list
	client.upload_file(directory + filename, bucketName, filename)

	print('File name: %s, Bucket name: %s' %(filename, bucketName))


def uploadVideo(videotopic, videoFile):
	print("Uploading video file: ", videoFile)
	session = boto3.Session(aws_access_key_id = AWS_ACCESS ,aws_secret_access_key = AWS_SECRET)
	client = session.client('s3')

	directory = os.popen('pwd').read().rstrip() + '/Camera' + '/'
	filenames = [os.path.basename(x) for x in glob.glob(str(directory) + '*{}*.avi'.format(videoFile))]

	for f in filenames:
		client.upload_file(directory+f, bucketName, f)

        print('File name: %s, Bucket name: %s' %(f,bucketName))


'''-------------------------- Save data --------------------------'''
# start the signal handler for power
signal.signal(signal.SIGINT, PoweroffEvent)

# read jsonschema file
schema_file = open('jsonschema_Rpi.json').read()
schema = yaml.load(schema_file)

# assign the starting distance values
preTime = datetime.strptime(TimeStamp(), ts)
cumdistance = 0.0

basicInfo = KeyInfo('raspberry1') # save key information
tripstart = basicInfo['trip_start']
message = basicInfo.copy()
message['event'] = 'CarVi activated'
print('trip_start : ', tripstart)

# upload 'CarVi activated' message to 'S3'
messageJson = json.dumps([message])
myAWSIoTMQTTClient.publish(topic, messageJson, 1)
if args.mode == 'publish':
        print('Published topic %s: %s\n' % (topic, messageJson))


# camera video
''' To record the video add [-cr T] '''
if camerarecord == 'T':
	tzone = datetime.now(timezone('America/Chicago'))
	cdtime = tzone.strftime(cts)
	cam_t = threading.Thread(target=CameraVideo, args=(cdtime,))
	cam_t.start()

line = gps.readline() # read the first gps line

gpsList = [] # save ALL sensor and gps data (default = 10 rows)

# geofence
zone_list = {}
zone_name = ["zone", "zone1", "zone2"]
zone_list["zone1"] = [(41.910979,-87.643464),(41.911362,-87.624839),(41.897691,-87.624238),(41.897819,-87.642777)]
zone_list["zone2"] = [(41.886894,-87.637027),(41.876222,-87.636941),(41.876030,-87.622350),(41.888874,-87.622865)]
zone_list["zone"] = [(-0.0001, 0.0001),(0.0001,0.0001), (0.0001,-0.0001),(-0.0001,-0.0001)]


# Publish to the same topic in a loop forever
while True:
	
    if args.mode == 'both' or args.mode == 'publish':
        
        message = basicInfo.copy()

        # GPS
        # check if the line start with '$GPRMC'. This is the first line of the gps data.
        if line.find('RMC') is -1 : line = gps.readline()
        else:
                msg = {}
                msg['gx'], msg['gy'], msg['gz'], msg['ax'], msg['ay'], msg['az'], msg['mx'], msg['my'],msg['mz'] = ([] for i in range(9)) 
		sensor_list = ["gz", "gy", "gx", "az", "ay", "ax", "mz", "my", "mx"]


                stopEvent = threading.Event()
                timeFinish = time.time() + 30
                stopEvent.clear
                while True:
                        q = Queue()
                        t = threading.Thread(target=SensorData, args=(stopEvent, timeFinish,q))
                        t.start()
                        t.result_queue = q
                        message.update(GPSReader(line)) # add gps data to message
                        line = gps.readline() # read next gps line
                        if line.find('GSV') > 0: # read gps last line
				message.update(GPSReader(line))
                                stopEvent.set()
				msg_new = {}
				try:
					for i in sensor_list:
						msg_new[i] = [sum(msg[i])/len(msg[i]), min(msg[i]), max(msg[i])]
				except: msg_new[i] = [0.0, 0.0, 0.0]
                                #message.update(msg)
				message.update(msg_new)
                                break # break if the message is full

		# change speed unit to km/hour
		if message['speed'] == None: message['speed'] = 0.0
		else : message['speed'] = float(message['speed'])*1.60934

                # GeoFence
		for zone in zone_name:
			if GeoFence(message['location'], zone_list[zone]):
				message['geofence'] = zone

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
                        currSpeed = round(message['speed']*1/3600,2) # conver into km
                        distance = currSpeed*((currTime - preTime).seconds)

                preTime = currTime
                cumdistance += distance
                message['distance'] = round(cumdistance, 4)
                gpsList.append(message)

		# check schema
		JsonSchema(message, schema)

		# upload data to 'S3'
		messageJson = json.dumps([message])

		myAWSIoTMQTTClient.publish(topic, messageJson, 1)
		if args.mode == 'publish':
			print('Published topic %s: %s\n' % (topic, messageJson))


                ###################### save as local file #####################################
                # save 'gpsList' as a local file (this json file has 10 rows)
                if len(gpsList) == 10:
                        try:
                                print('Dumping')
                                with open("GPS_DATA_{}.txt".format(cdtime), mode='a+') as f:
                                        json.dump(gpsList, f)
					json.dump(',', f)
                                        gpsList = [] # reset 'gpsList'
                        except: print('')
                ###############################################################################

