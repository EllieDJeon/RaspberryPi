# Setup RPi (language, local, wifi)  
Once we start up the RPi, the defualt settings might not be in US (keyboard, time, or locale) We can change the setting on RPi.  


### 1. Language
### 2. Locale/Keyboard
### 3. Wifi
	
  Enter following and see if you see 'wlan0'; RPi is able to scan wifi.  

  ```
  sudo iwconfig  
  sudo iwlist wlan0 scan
  ```  

  ` sudo nano /etc/wpa_sipplicant/wpa_supplicant.conf`  

  Edit and save the file with wifi name and password that you want to use.  
  For exmaple, if wifi name is _'iptime'_ and password is _'PASSWORTD'_ you would edit:  

  ```
    network={
    ssid="iptime"
    psk="PASSWORD"
    key_mgmt=WPA-PSK
    }
  ```

  

