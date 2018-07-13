# Camera with Raspberry Pi 3  

## Contents  
>### 1. Set camera on RPi3  
>### 2. Installation  
>### 3. Usage camera (photo and video)  
<br>  

## 1. Set camera on RPi3  
We can use any standard USB webcam to take pictures and video.  

### Parts List  
-standard USB webcam  

## 2. Installation  
We need two python module to take pictures and record video. `fswebcam` will be used for taking and saving pictures and `libav=tools` will be recording the video and saving it on the RPi3.  


Install `fswebcam` and `libav=tools` on RPi3.  
```
sudo apt-get install fswebcam
sudo apt-get install libav-tools  
```  
<br>  


## 3. Usage (pictures and video)  
Pictures and video can be taken and saved by using following commends. First, we want to create a directory to save files.  
'mkdir RPicam'  


Pictures  
``` 
fswebcam Rpi_picture.jpg
```
We can also specify the resolution how the picture to be taken at with the commend below.  
```  
fswebcam -r 1280x720 Rpi_picture2.jpg  
fswebcam -r 1280x720 --no-banner image3.jpg  

```  

Video  
``` 
```







mkdir camera  
fswebcam image.jpg  

#install avconv  
sudo apt-get install libav-tools  

#taking video  
avconv -f video4linux2 -r 25 -s 1280x960 -i /dev/video0 ~/aws-iot-device-sdk-python/samples/testKits/camera/VideoStream.avi  

#recording video  
omxplayer ~/aws-iot-device-sdk-python/samples/testKits/camera/VideoStream.avi  



https://www.raspberrypi.org/documentation/usage/webcams/  

https://hub.packtpub.com/working-webcam-and-pi-camera/  
https://dototot.com/how-to-extract-images-from-a-video-with-avconv-on-linux/  
