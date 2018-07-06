import threading
import time
import queue


def sensor(stopEvent, timeFinish, arg, q):
    msg['ax'] = []
    while not stopEvent.is_set():
        while time.time() < timeFinish:
            print ("working on %s" % arg)
            time.sleep(1)            
            msg['ax'].append(1)
            q.put(msg)
            if stopEvent.is_set():
                print("stop events accur: break 'sensor' ")
#                return msg
                break
        if time.time() > timeFinish:
                print("time limit exceeded")
                stopEvent.set()
    print("Stopping as you wish.")


def gps(stopEvent, timeFinish):
    q = queue.Queue()

    t = threading.Thread(target=sensor, args=(stopEvent, timeFinish, "sensor",q))
    t.start()
    t.result_queue = q        
    print(t)    
    #print("MAIN - sleep(5)")
    time.sleep(5)
    msg = {}
    msg['speed'] = 17.0
    print("setting stopEvent on gps")
    stopEvent.set()
    #print("MAIN - sleep(10)")
    return msg
    #time.sleep(10)
    #print("MAIN - exiting...")

msg = {}
stopEvent = threading.Event()
timeFinish = time.time() + 10

stopEvent.clear
print('GPS start')

msg.update(gps(stopEvent, timeFinish))
time.sleep(5)
print(msg)
stopEvent.set()


'''
msg = {}
stopEvent = threading.Event()
timeFinish = time.time() + 15

while True:
    stopEvent.clear
    print('GPS start')
    
    msg.update(gps(stopEvent, timeFinish))
    time.sleep(5)
    print(msg)
    stopEvent.set()
'''   

