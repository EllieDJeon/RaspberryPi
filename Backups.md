# Backup Raspberry Pi
<br>
## 1. Home folder  
You can keep _RPi home folder_ by using the following command. This creates a tar archive and you keep a copy of it on our home PC or in cloud storage. The following commands will create `pi_home.tar.gz` in `/home/`.
```
cd /home/
sudo tar czf pi_home.tar.gz pi
```
<br>


## 2. SD card  
(Note that this option is written for Windows based computer or linux computers.)  

2-1. Install 'Win32Disklmager'  
We can simply backup the SD card from your Raspberry Pi. __'Win32DiskImager'__ is the program that can read the image and write it back to the SD card. Download the program and extract it on your computer. [(Download)](https://sourceforge.net/projects/win32diskimager/)  

Once the program is ready, simply follow a step-by-step guide shown below.  
<br>

2-2. Backup Raspberry Pi  
To backup your Raspberry Pi, you need __the SD card from the Raspberry Pi__ and the __Windows computer with a SD card reader__.  

> __STEPS__  
> 
>1. Insert the SD card into your computer.  
>2. Start the 'Win32Disklmager' program.  
>3. Once started, selected the SD card drive.   
>*(Make sure you select the right drive that is being backed up.)*  
>4. Press the folder button and locate the folder where to put your backup.  
>5. Once you are in the right folder, write the name of your backup and press "Open".  
>6. Press "Read" to read the SD card into the image file. This process will take a few minutes.  
>*(__Do not click "Write"__ since it will __overwrite your SD card.__)*   
<br>


2-3. Restore Raspberry Pi  
To restore a SD card backup, you need __a SD card__ and __'Win32Disklmager' program__. Follow the steps below.

> __STEPS__  
> 
>1. Plug-in your SD card into the computer.  
>2. Start the 'Win32Disklmager' program.  
>3. Press the folder under "Image file" and select your backup image.  
>4. Select the drive of your SD card under "Device".  
>(*Make sure you select __the right drive that is your SD card.__*)
>5.  Press "Write" and wait while the program restores the backup on your SD card. Once the process is done, unplug the SD card and plug it into the Raspberry Pi.
<br>



