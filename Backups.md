# Backup Raspberry Pi
## 1. Home folder  
You can keep _RPi home folder_ by using the following command. This creates a tar archive and you keep a copy of it on our home PC or in cloud storage. The following commands will create `pi_home.tar.gz` in `/home/`.
```
cd /home/
sudo tar czf pi_home.tar.gz pi
```

## 2. SD card  
(Note that this option is written for Windows based computer or linux computers.)  

### 2-1. Install 'Win32Disklmager'  
We can simply backup the SD card from your Raspberry Pi. __'Win32DiskImager'__ is the program that can read the image and write it back to the SD card. Download the program and extract it on your computer. [(Download)](https://sourceforge.net/projects/win32diskimager/)  


### 2-2. Backup Raspberry Pi  
1.Insert the SD card into your computer  
2.Start the 'Win32Disklmager' program  
3.Once started, selected the SD card drive (Make sure you select the right drive that is being backed up)  
4.Press the folder button and locate the folder where to put your backup  
5.Once you are in the right folder, write the name of your backup and press "Open"  
6.Press "Read" to read the SD card into the image file (Make sure you __do not click "Write"__ since it will __overwrite your SD card.__)  This process will take a few minutes.


### 2-3. Restore Raspberry Pi  
1.Plug-in your SD card into the computer  
2.Start the 'Win32Disklmager' program  
3.Press the folder under "Image file" and select your backup image  
4.Select the drive of your SD card under "Device"  
(
5. 

