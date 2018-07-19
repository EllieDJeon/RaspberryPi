# =============================================================================
# signal
# =============================================================================
 
import signal, sys, time
# time
from datetime import datetime
from pytz import timezone
ts = "%Y-%m-%d %H:%M:%S"
cts = "%Y%m%d_%H%M%S"
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

def PoweroffEvent(signal, frame):
    print('Ctrl+C received: Power off')
    global basicInfo
    message = basicInfo.copy()
    message['event'] = 'Power Off'
    print(message)

    '''
    # upload 'Power Off' message to 'S3'
    messageJson = json.dumps([message])
    myAWSIoTMQTTClient.publish(topic, messageJson, 1)
    if args.mode == 'publish':
        print('Published topic %s: %s\n' % (topic, messageJson))
    '''
    time.sleep(1)
    sys.exit(0)
    
basicInfo = KeyInfo('raspberry1') # save key informationsignal.signal(signal.SIGINT, PoweroffEvent)
signal.signal(signal.SIGINT, PoweroffEvent)

while(True): 
    time.sleep(1)     
    print('while loop')   
