# USB webcam on Raspberry Pi 3  

## Contents  
>### 1. Set webcam on RPi3  
>### 2. Installation  
>### 3. Usage (photo and video)  
<br>  

## 1. Set webcam on RPi3  
We can use any standard USB webcam to take pictures and video.  

### Parts List  
-standard USB webcam  
<br>  

## 2. Installation  
We need two python module to take pictures and record video. `fswebcam` will be used for taking and saving pictures and `libav=tools` will be recording the video and saving it on the RPi3.  


Install `fswebcam` and `libav=tools` on RPi3.  
```
sudo apt-get install fswebcam
sudo apt-get install libav-tools  
```  
<br>  


## 3. Usage (pictures and video)  
Pictures and video can be taken and saved by using following commands. First, we want to create a directory to save files.  
'mkdir RPicam'  


- __Pictures__  
Following command will take a picture and save it as a jpg file named __'Rpi_picture.jpg__.   
``` 
fswebcam Rpi_picture.jpg
```  

We can also specify the resolution how the picture to be taken at with the command below.  
```  
fswebcam -r 1280x720 Rpi_picture2.jpg  
fswebcam -r 1280x720 --no-banner Rpi_picture3.jpg  

```  


- __Video__  
We can record and save live videos using `avconc`. Run the following command to record a video. Presse _'Ctrl + C'_ to terminate the recording.  
``` 
avconv -f video4linux2 -r 25 -s 1280x960 -i /dev/video0 ~/aws-iot-device-sdk-python/samples/testKits/camera/Rpi_video.avi  
```  

To play the recorded video, run the following command.  
```  
omxplayer ~/aws-iot-device-sdk-python/samples/testKits/camera/Rpi_video.avi  
```  
<br>  
<br>  



Resources:  
https://www.raspberrypi.org/documentation/usage/webcams/  

https://hub.packtpub.com/working-webcam-and-pi-camera/  
https://dototot.com/how-to-extract-images-from-a-video-with-avconv-on-linux/  
