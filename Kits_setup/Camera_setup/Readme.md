mkdir camera  
fswebcam image.jpg  

#install avconv  
sudo apt-get install libav-tools  

#taking video  
avconv -f video4linux2 -r 25 -s 1280x960 -i /dev/video0 ~/aws-iot-device-sdk-python/samples/testKits/camera/VideoStream.avi  

#streaming video  
omxplayer ~/aws-iot-device-sdk-python/samples/testKits/camera/VideoStream.avi  



https://www.raspberrypi.org/documentation/usage/webcams/  

https://hub.packtpub.com/working-webcam-and-pi-camera/  
https://dototot.com/how-to-extract-images-from-a-video-with-avconv-on-linux/  
