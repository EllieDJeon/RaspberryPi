import serial
import json
gps = serial.Serial("/dev/ttyUSB0", baudrate = 9600)
gpsList = []
while True:
	line = gps.readline()
	data = line.split(",")
	
	if data[0] == '$GPRMC' and data[2] == "A":
		gpsdata = {"TimeStamp":data[1], "Latitude":data[3],"NS":data[4], "Longitude":data[5],"EW":data[6]}
	if data[0] == '$GPGGA' : 
		gpsdata["Altitude"] = data[7]
		gpsdata["Satellites"] = data[5] # 5 satellites are in view
	if data[0] == '$GPHDT': gpsdata["Heading"] = data[1]
	if data[0] == '$GPVTG' : gpsdata["Speed_km"] = data[7] # speed over ground in kilometer/hour
		# data[5] = Speed over ground in knots
        gpsList.append(gpsdata)
	print(len(gpsList))
	
	if len(gpsList) == 10:
		with open("GPS_DATA.json", mode='a') as f:
		json.dump(gpsList, f)
		f.write("\n")
		gpsList = []
		print("File Successed")

#			with open("GPS_DATA.json", mode='a') as f:
#				for g in gpsList:
#					json.dumps(g, f)
#					f.write("\n")
#				gpsList = []
#                               print("File Successed")



