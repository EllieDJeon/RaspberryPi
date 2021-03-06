# **RaspberryPi** 

Sending the sensor data from __RaspberryPi__ to __AWS__  

## **Table of Contents** 

1. Introduction
2. Installation
3. Modules
   - argparse 
   - SenseHat
4. Implementation  


## 1. Introduction

The original[ _BasicPubSub.py_](https://github.com/aws/aws-iot-device-sdk-python) that you can utilize with RaspberryPi shows a output of “Hello, world!” message. We updated it to show the outputs of _accelerometer, gyroscope, magnetometer, airpressure, temperature,_ and _humidity._

## 2. Installation

### 2-1. Download the file
```
$ git clone https://github.com/aws/aws-iot-device-sdk-python.git  
$ cd aws-iot-device-sdk-python  
$ python setup.py install
```
Note: You may receive errors about not having permissions to install the SDK. If that is the case, run the command as root:  
```
$ sudo chown -R $USER /usr/local/lib/python2.7
$ sudo python setup.py install 
```

### 2-2. Copy Your Certs and Key File to PubSub Directory.  
```
$ aws-iot-device-sdk-python/samples/basicPubSub
```

__Copy the following files:__  
```
xxxxxxxxxx-certificate.pem.crt  
xxxxxxxxxx-private.pem.key  
root-CA.pem  
```  

__to the above directory:__  
```
$ cp <cert location> aws-iot-device-sdk-python/samples/basicPubSub  
$ cp <priv key location> aws-iot-device-sdk-python/samples/basicPubSub  
$ cp <root CA location> aws-iot-device-sdk-python/samples/basicPubSub  
```  

### 2-3 Command the file

To run this python file, 
```
python <your_file_name> -e <endpoint> -r <rootCA> -c <certificate_key> - k <private_key>
```


## 3. Module and Function   
### 3-1. `argparse`
you can use this module to wrtie user-friendly command-line interfaces. In our case, we can translate the outputs that RaspberryPi generates into user-friendly command-line interfaces.  

### 3-1-0. Prerequisites
```
import argparse
parser = argparse.ArgumentParser()
```  

### 3-1-1. Add arguments
Before reading the sensor data, you can define what arguments it requires. We added 
```
parser.add_argument("-A", "--accelerometer", action="store_true", default=False)
parser.add_argument('-G','--gyroscope', action='store_true', default=False)
parser.add_argument('-Ma','--magnetometer', action='store_true', default=False)

parser.add_argument("-P", "--airpressure", action="store_true", default=False)
parser.add_argument("-T", "--temperature", action="store_true", default=False)
parser.add_argument('-H','--humidity', action='store_true', default=False)
```  

  
### 3-2. `SenseHat`
The SenseHat controls the RaspberryPi Senses. In our case, we added to detect the seneses of _accelerometer, gyroscope, magnetometer, airpressure, temperature,_ and _humidity._
 

| Sensor | Code | Unit |
| ---      | ---       | ---       |
| Gyroscope (Pitch, Roll, Yaw) | `get_orientation()`| °/s       |
| Accelerometer (ax, ay, az) | `get_accelerometer_raw()` | m/s^2       |
| Magnetometer (mx, my, mz) | `get_compass_raw()` | microtesla (µT)       |
| Pressure | `get_pressure()` | hPa       |
| Temperature | `get_temperature()` | °C       |
| Humidity | `get_humidity()` | %       |  



### 3-2-0. Prerequisites  
For the test code-examples, `SenseHat` and `time` modules are used. `time` module is used for the time intervals on outputting the values.

```ruby
from sense_hat import SenseHat
import time

sense = SenseHat()
sense.clear()
```  

### 3-2-1. Gyroscope (Pitch, Roll, Yaw)  
The `get_orientation()` function obtains the three degrees of Gyroscope as a numerical value. These returns in Python's dictionary.  

__Code-Example__ 
```ruby
pitch, roll, yaw = sense.get_orientation().values()
print("pitch=%s, roll=%s, yaw=%s" % (pitch, roll, yaw))
```  

### 3-2-2. Accelerometer (ax, ay, az)
Acceleration sensor detects the acceleration in the direction of the ground due to gravity. The `get_accelerometer_raw()` function obtains the component of each spatial axis in a three dimensional space as a numerical value. These returns in Python's dictionary.  

__Code-Example__
```ruby
ax, ay, az = sense.get_accelerometer_raw().values()
print("ax=%s, ay=%s, ax=%s" % (ax, ay, az))
```  
  
### 3-2-3. Magnetometer (mx, my, mz)
Magnetometer sensor detects the direction of North from the magnetometer in degrees. The `get_compass_raw()` function obtains the raw x, y and z axis magnetometer data as a numerical value. These returns in Python's dictionary.  

__Code-Example__
```ruby
mx, my, mz = sense.get_compass_raw().values()
print("mx=%s, my=%s, mx=%s" % (mx, my, mz))
```  
  
### 3-2-4. Pressure
The `get_pressure()` function obtains the current pressure in Millibars from the pressure sensor. These returns a numerical value in float.  

__Code-Example__
```ruby
pressure = sense.get_pressure()
```  

### 3-2-5. Temperature
The `get_temperature()` function obtains the current temperature in degrees Celsius. These returns a numerical value in float.   

__Code-Example__
```ruby
temp = sense.get_temperature()
```  

### 3-2-6. Humidity
The `get_humidity()` function obtains the percentage of relative humidity from the humidity sensor. These returns a numerical value in float.  

__Code-Example__
```ruby
humidity = sense.get_humidity()
```  


## 4. Implementation

Assign the saved sensor data to the `message` dictionary and publish to the topic in a while-loop.  

```ruby
while True:
    if args.mode == 'both' or args.mode == 'publish':
        message = {}
        
        message['gx'] = pitch
        message['gy'] = roll
        message['gz'] = yaw
        
        message['ax'] = ax
        message['ay'] = ay
        message['az'] = az

        message['mx'] = mx
        message['my'] = my
        message['mz'] = mz
        
        message['pressure'] = pressure
        message['temperature'] = temp
        message['humidity'] = humidity
        
        message['message'] = 'SENSOR DETECTED'
         
        messageJson = json.dumps(message)
        myAWSIoTMQTTClient.publish(topic, messageJson, 1)
        if args.mode == 'publish':
            print('Published topic %s: %s\n' % (topic, messageJson))
```  

