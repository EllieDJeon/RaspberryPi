# GPS on Raspberry Pi 3  

## Contents  
>### 1. Set parts  
>### 2. Set GPS on RPi3 
>### 3. GPS Data Overview and Python Code  
<br>


## 1. Set parts  

### Parts List  
-Raspberry Pi 3  
-GPS breakout ()
-USB to TLL Serial cable  

### GPS using USB to TTL
Attach the wires from the USB to TLL cable to the GPS breakout:  

| Cable | GPS breakout |   
|:-----------:|:-----------:|  
| Red | VCC |  
| Black | GND |  
| Green | RX |  
| White | TX |  

Once the cable is ready, insert the USB part of the cable into the RPi3. 
<br>

 
## 2. Set GPS on RPi3 

### Installing gpsd (GPS daemon)  
'gpsd' is a service deamon that monitors CPS or AIS receivers attached to a host computer through serial or USB ports.  
 For the more information: http://catb.org/gpsd/.  

Install 'gpsd' and disable the gpsd systemd service.  
```
sudo apt-get install gpsd gpsd-clients python-gps  
sudo systemctl stop gpsd.socket  
sudo systemctl disable gpsd.socket  
```  

The gpsd needs to be started and pointed at the USB device (or UART).  
`sudo killall gpsd`  


USB to TLL use `sudo gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock`  
UART use `sudo gpsd /dev/ttyS0 -F /var/run/gpsd.sock`  


### Checking USB and testing 'gpsd'  
We should select which USB is going to be used by the GPS.  
Following command lists the conndected USB devices (You will see _/dev/ttyUSB0_ typically.):  
`ls /dev/ttyUSB*`  
 
 You can list all USB devices with `sudo lsusb`.  
 
 
 Point 'gpsd' to the USB device.  
 ```
 sudo killall gpsd
 sudo cat /dev/ttyUSB0
 sudo gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock  
  ```  
  
  You can check the lists with `sudo cat /dev/ttyUSB0`.  
  Run `cgps` or `gpsmon` to test and monitor a live-streaming update of GPS data.  
  
  
  
![ ](https://github.com/EllieDJeon/RaspberryPi/IMG/gps_1.PNG)  


> __Note__  
> If `cgps` does not work, repeat the commands below:
> ```
> sudo systemctl stop gpsd.socket  
> sudo systemctl disable gpsd.socket
> ```  
> then run `sudo gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock`.  
> now rerun `cgps`.    


## 3. GPS Data Overview and Python Code (gps3, pynmea2)  

* gps3  
```  
sudo pip3 install gps3  
sudo apt-get install python3-microstacknode  
sudo apt-get install python3-serial  
```  

* [pynmea2](https://github.com/Knio/pynmea2/blob/master/README.md)  
The NMEASentence object has different properties, depending on its sentence type. pynmea2 is a python library for the NMEA 0183 protocol. `parse(data)` will read individual NMEA sentences which start with '$'.   
```  
pip install pynmea2  
```  


### '$GPxxx' sentence codes and descriptions  
We are using following sentence codes and GPS data:   

| NMEA | DATA |   
|:-----------:|:-----------|  
| $GPRMC | Time, Navigate warning, Latitude, Longitude, Speed(miles/h) |  
| $GPHDT | Heading |  
| $GPVTG | Speed(km/h), Speed(miles/h) |  
| $GPGGA | Altitude |  


example:  
```  
>>> import serial  
>>> import pynmea2  
>>> gps = serial.Serial("/dev/ttyUSB0", baudrate = 9600, timeout=10000)  
>>> gpsLine = gps.readline() # read the gps line  
>>> gpsLine  
"$GPGGA,184353.07,1929.045,S,02410.506,E,1,04,2.6,100.00,M,-33.9,M,,0000*6D"  
>>> gpsData = pynmea2.parse(gpsLine)  
>>> gpsData  
<GGA(timestamp=datetime.time(18, 43, 53), lat='1929.045', lat_dir='S', lon='02410.506', lon_dir='E', gps_qual='1', num_sats='04', horizontal_dil='2.6', altitude=100.0, altitude_units='M', geo_sep='-33.9', geo_sep_units='M', age_gps_data='', ref_station_id='0000')>  
>>>  gpsData.lon  
'02410.506'  
```

More info about NMEA Syntax GPS: http://aprs.gids.nl/nmea/#rmc


 
References:  
http://www.intellamech.com/RaspberryPi-projects/rpi3_gps.html#_gps_using_usb_to_tll  


