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
import serial
gps = serial.Serial("/dev/ttyUSB0", baudrate = 9600)

# time
from datetime import datetime 
from pytz import timezone
ts = "%Y-%m-%d %H:%M:%S"



def loca_format(coord):
    # DDDMM.MMMMM -> DD.MMMM 
    # "location":"41.8923,-87.6155"
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

# Publish to the same topic in a loop forever
while True:
	
    gpsList = [] # save ALL sensor and gps data (10 rows)
    if args.mode == 'both' or args.mode == 'publish':
        
        pitch, roll, yaw = sense.get_orientation().values()
        ax, ay, az = sense.get_accelerometer_raw().values()
        mx, my, mz = sense.get_compass_raw().values()
        
        
        message = {}

        message['camera_id'] = 'raspberry1'
        
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
        
        # time_stamp
        chi_tz = datetime.now(timezone('America/Chicago'))
        chi_dt = chi_tz.strftime(ts)
        message['time_stamp'] = chi_dt
        
        
        # Button
        button = Button(25)
        button = Button(25, debounce=1.0)
        buttonPress = button.is_pressed()
        
        message['emergencyCall'] = buttonPress
        
        # GPS
        data = [] # save one time gps(one row) from 8 different sentences
        while True:
		line = gps.readline()
		rawgps = line.split(",")
		data.append(rawgps)
            
            
            	# once meet sentence' $GPZDA, collecting messages that we need
		if rawgps[0] == '$GPZDA': break

	if data[0][2] == "A":
	#message['TimeStamp'] = data[0][1]
		message['location'] = loca_format(data[0][3]) + "," + loca_format(data[0][5])
		message['location_raw'] = data[0][3] + "," + data[0][5]
		message['NS'] = data[0][4]
		message['EW'] = data[0][6]
		message['speed'] = data[0][7]
		message['Altitude'] = data[2][7]
		message['Satellites'] = data[2][5] # 5 satellit

		# append one message(row) to 'gpsList' and reset the 'data'
		gpsList.append(message)
		data = []
                    
###################### save as local file #####################################
                    # save 'gpsList' as a local file (this json file has 10 rows)
		if len(gpsList) == 10:
			with open("GPS_DATA.txt", mode='a') as f:
				json.dump(gpsList, f)
				f.write("\n")
				gpsList = [] # reset 'gpsList'
###############################################################################

		# upload data to 'S3'
		messageJson = json.dumps(message)
		myAWSIoTMQTTClient.publish(topic, messageJson, 1)
		if args.mode == 'publish':
			print('Published topic %s: %s\n' % (topic, messageJson))
