'''
/*
 * Copyright 2010-2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTThingJobsClient
from AWSIoTPythonSDK.core.jobs.thingJobManager import jobExecutionTopicType
from AWSIoTPythonSDK.core.jobs.thingJobManager import jobExecutionTopicReplyType
from AWSIoTPythonSDK.core.jobs.thingJobManager import jobExecutionStatus

import threading
import logging
import time
import datetime
import argparse
import json

class JobsMessageProcessor(object):
    def __init__(self, awsIoTMQTTThingJobsClient, clientToken):
        #keep track of this to correlate request/responses
        self.clientToken = clientToken
        self.awsIoTMQTTThingJobsClient = awsIoTMQTTThingJobsClient
        self.done = False
        self.jobsStarted = 0
        self.jobsSucceeded = 0
        self.jobsRejected = 0
        self._setupCallbacks(self.awsIoTMQTTThingJobsClient)

    def _setupCallbacks(self, awsIoTMQTTThingJobsClient):
        self.awsIoTMQTTThingJobsClient.createJobSubscription(self.newJobReceived, jobExecutionTopicType.JOB_NOTIFY_NEXT_TOPIC)
        self.awsIoTMQTTThingJobsClient.createJobSubscription(self.startNextJobSuccessfullyInProgress, jobExecutionTopicType.JOB_START_NEXT_TOPIC, jobExecutionTopicReplyType.JOB_ACCEPTED_REPLY_TYPE)
        self.awsIoTMQTTThingJobsClient.createJobSubscription(self.startNextRejected, jobExecutionTopicType.JOB_START_NEXT_TOPIC, jobExecutionTopicReplyType.JOB_REJECTED_REPLY_TYPE)

        # '+' indicates a wildcard for jobId in the following subscriptions
        self.awsIoTMQTTThingJobsClient.createJobSubscription(self.updateJobSuccessful, jobExecutionTopicType.JOB_UPDATE_TOPIC, jobExecutionTopicReplyType.JOB_ACCEPTED_REPLY_TYPE, '+')
        self.awsIoTMQTTThingJobsClient.createJobSubscription(self.updateJobRejected, jobExecutionTopicType.JOB_UPDATE_TOPIC, jobExecutionTopicReplyType.JOB_REJECTED_REPLY_TYPE, '+')

    #call back on successful job updates
    def startNextJobSuccessfullyInProgress(self, client, userdata, message):
        payload = json.loads(message.payload.decode('utf-8'))
        if 'execution' in payload:
            self.jobsStarted += 1
            execution = payload['execution']
            self.executeJob(execution)
            statusDetails = {'HandledBy': 'ClientToken: {}'.format(self.clientToken)}
            threading.Thread(target = self.awsIoTMQTTThingJobsClient.sendJobsUpdate, kwargs = {'jobId': execution['jobId'], 'status': jobExecutionStatus.JOB_EXECUTION_SUCCEEDED, 'statusDetails': statusDetails, 'expectedVersion': execution['versionNumber'], 'executionNumber': execution['executionNumber']}).start()
        else:
            print('Start next saw no execution: ' + message.payload.decode('utf-8'))
            self.done = True

    def executeJob(self, execution):
        print('Executing job ID, version, number: {}, {}, {}'.format(execution['jobId'], execution['versionNumber'], execution['executionNumber']))
        print('With jobDocument: ' + json.dumps(execution['jobDocument']))

    def newJobReceived(self, client, userdata, message):
        payload = json.loads(message.payload.decode('utf-8'))
        if 'execution' in payload:
            self._attemptStartNextJob()
        else:
            print('Notify next saw no execution')
            self.done = True

    def processJobs(self):
        self.done = False
        self._attemptStartNextJob()

    def startNextRejected(self, client, userdata, message):
        printf('Start next rejected:' + message.payload.decode('utf-8'))
        self.jobsRejected += 1

    def updateJobSuccessful(self, client, userdata, message):
        self.jobsSucceeded += 1

    def updateJobRejected(self, client, userdata, message):
        self.jobsRejected += 1

    def _attemptStartNextJob(self):
        statusDetails = {'StartedBy': 'ClientToken: {} on {}'.format(self.clientToken, datetime.datetime.now().isoformat())}
        threading.Thread(target=self.awsIoTMQTTThingJobsClient.sendJobsStartNext, kwargs = {'statusDetails': statusDetails}).start()

    def isDone(self):
        return self.done

    def getStats(self):
        stats = {}
        stats['jobsStarted'] = self.jobsStarted
        stats['jobsSucceeded'] = self.jobsSucceeded
        stats['jobsRejected'] = self.jobsRejected
        return stats

def DownloadFile(directory, KEY, BUCKET_NAME, FILE_NAME):
    if directory: os.chdir(directory)
    else: directory = os.popen('pwd').read().rstrip() + '/'

    try:
        s3.Bucket(BUCKET_NAME).download_file(KEY, FILE_NAME)
	jobsMsgProc.processJobs()
        print("File downloaded")
        print("File: %s" %(directory+FILE_NAME))
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise

def GetJobInfo(JOBID):
        # get the job and job document information
        info_job = iot.describe_job(jobId=JOBID) # job info
        info_job_doc = iot.get_job_document(jobId=JOBID)
        job_doc_dict = ast.literal_eval(info_job_doc['document']) # job doc info

        print("New Job is created!")
        print("===========================================================================")
        print("Job name: %s" %JOBID)
        print("Target: %s" %TARGET)
        print("Status: %s" %info_job['job']['status'])
        print("Document Sourse: \n%s" %info_job['documentSource'])
        print("Document:")
        print(job_doc_dict)
        print("Responses:")
        print()
        return info_job, job_doc_dict

def VersionUpdate(directory, CURR_IMG_FILE):
    if directory: os.chdir(directory)
    else: directory = os.popen('pwd').read().rstrip() + '/'+ 'raspJob/'

    filenames = [os.path.basename(x) for x in glob.glob(str(directory) + '*{}'.format(CURR_IMG_FILE))]
    curr_version = filenames[0].split('.')[:]
    NEW_ver = int(info_job_doc['firmware']['version'])
    CURR_ver = int(curr_version[0][-2:])
    print("New Version: %d" %NEW_ver)
    print("Current Version: %d" %CURR_ver)
    print()
    
    if NEW_ver > CURR_ver : 
        print("New Version available!")
        DownloadFile(directory, IMG_KEY, IMG_BUCKET_NAME, 'rasp_img_{}.txt'.format(NEW_ver))
        print("Updating Version ...")
        print("=======================")
        while info_job['job']['status'] == 'IN_PROGRESS':
            print(info_job['job']['status']+'...')
            time.sleep(10)
        print()
        print("Updating Statue: %s" %info_job['job']['status'])
        print()
    else: print("Latest Version!")


# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--thingName", action="store", dest="thingName", help="Your AWS IoT ThingName to process jobs for")
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
parser.add_argument("-p", "--port", action="store", dest="port", type=int, help="Port number override")
parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                    help="Use MQTT over WebSocket")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicJobsSampleClient",
                    help="Targeted client id")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
port = args.port
useWebsocket = args.useWebsocket
clientId = args.clientId
thingName = args.thingName

if args.useWebsocket and args.certificatePath and args.privateKeyPath:
    parser.error("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
    exit(2)

if not args.useWebsocket and (not args.certificatePath or not args.privateKeyPath):
    parser.error("Missing credentials for authentication.")
    exit(2)

# Port defaults
if args.useWebsocket and not args.port:  # When no port override for WebSocket, default to 443
    port = 443
if not args.useWebsocket and not args.port:  # When no port override for non-WebSocket, default to 8883
    port = 8883

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
    myAWSIoTMQTTClient.configureEndpoint(host, port)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath)
else:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
    myAWSIoTMQTTClient.configureEndpoint(host, port)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(10)  # 5 sec

jobsClient = AWSIoTMQTTThingJobsClient(clientId, thingName, QoS=1, awsIoTMQTTClient=myAWSIoTMQTTClient)

print('Connecting to MQTT server and setting up callbacks...')
jobsClient.connect()

# AWS access
AWS_ACCESS = 'AKIAICFM4F6PFMZG4JKQ'
AWS_SECRET = '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'

# IMG and job information
S3_REGION = 'us-west-2'
IMG_BUCKET_NAME = 'rasp-img-files'
IMG_KEY = 'rasp_img_1.0.1.txt'

JOB_BUCKET_NAME = 'rasp-job-document'
JOB_DOC = 'rasp_job_doc.json'

directory = os.popen('pwd').read().rstrip() + '/'+ 'raspJob/'
# open S3 session with AWS access
session = boto3.Session(aws_access_key_id = AWS_ACCESS ,aws_secret_access_key = AWS_SECRET)
s3 = session.resource('s3')

client = session.client('s3')


iot = session.client('iot', region_name = S3_REGION) # region name is from the endpoint of iot

# params
JOBID = 'rasp-2-job-test-2'
TARGET = 'arn:aws:iot:us-west-2:702738637364:thing/RasberryPi_2'

#GetJobInfo(JOBID)
info_job, info_job_doc = GetJobInfo(JOBID)
NEW_ver = int(info_job_doc['firmware']['version'])

CURR_IMG_FILE = 'rasp_img_19.txt'
CURR_ver = int(curr_version[0][-2:])
jobsMsgProc = JobsMessageProcessor(jobsClient, clientId)
print('Starting to process jobs...')


print("New Version: %d" %NEW_ver)
print("Current Version: %d" %CURR_ver)
print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

if NEW_ver > CURR_ver : 
	print("New Version available!")
	print()
	jobsMsgProc = JobsMessageProcessor(jobsClient, clientId)
	print('Starting to process jobs...')
	DownloadFile(directory, IMG_KEY, IMG_BUCKET_NAME, 'rasp_img_{}.txt'.format(NEW_ver))
	#jobsMsgProc.processJobs()
	while not jobsMsgProc.isDone():
		print(info_job['job']['status'],'...')
            	time.sleep(10)
        print()
        print("Updated Statue: %s" %info_job['job']['status'])
        print()
elif NEW_ver == CURR_ver : print("Latest Version!")

''' 
jobsMsgProc = JobsMessageProcessor(jobsClient, clientId)
print('Starting to process jobs...')
jobsMsgProc.processJobs()
while not jobsMsgProc.isDone():
    time.sleep(2)
'''

print('Done processing jobs')
print('Stats: ' + json.dumps(jobsMsgProc.getStats()))

jobsClient.disconnect()
