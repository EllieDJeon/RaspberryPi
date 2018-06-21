# GPS on Raspberry Pi 3  

## 1. Set parts  

### Parts List  
-Raspberry Pi 3  
-GPS breakout ()
-USB to TLL Serial cable  

### GPS using USB to TTL
Attach the wires from the USB to TLL cable to the GPS breakout:  
> Cable  GPS breakout  
> Red to VCC  
> Black to GND  
> Green to RX  
> White to TX  

Once the cable is ready, insert the USB part of the cable into the RPi3. 

 
## 2. Set GPS on RPi3 

### Installing gpsd (GPS daemon)  
'gpsd' is a service deamon that monitors CPS or AIS receivers attached to a host computer through serial or USB ports. For the more information: http://catb.org/gpsd/.  

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
 sudo gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock  
  ```  
  
  Run `cgps` to test.  



## 3. Python Code  
```  
sudo pip3 install gps3  
sudo apt-get install python3-microstacknode  
sudo apt-get install python3-serial  
```  


 
References:  
http://www.intellamech.com/RaspberryPi-projects/rpi3_gps.html#_gps_using_usb_to_tll  

