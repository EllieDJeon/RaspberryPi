import serial
import json
gps = serial.Serial("/dev/ttyUSB0", baudrate = 9600)
gpsList = []
while True:
	line = gps.readline()
	data = line.split(",")
	
	if data[0] == '$GPRMC' and data[2] == "A":
		gpsdata = {"TimeStamp":data[1], "Latitude":data[3], "Longitude":data[5], "NS":data[4], "EW":data[6]}
                gpsList.append(gpsdata)
		print(len(gpsList))
		if len(gpsList) == 10:

#			with open("GPS_DATA.json", mode='a') as f:
#				for g in gpsList:
#					json.dumps(g, f)
#					f.write("\n")
#				gpsList = []
#                               print("File Successed")


			with open("GPS_DATA.json", mode='a') as f:
				json.dump(gpsList, f)
				f.write("\n")
				gpsList = []
				print("File Successed")
