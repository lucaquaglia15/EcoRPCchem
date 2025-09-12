import socket
import re
import time
from datetime import datetime
from labjack import ljm
import mysql.connector
from hvl_ccb.dev.labjack import LabJack
from dotenv import dotenv_values
import smbus2
import bme280

#Read environmental temperature/pressure/humidity via BME280
def readEnv():
	# BME280 sensor address (default address)
	address = 0x76

	# Initialize I2C bus
	bus = smbus2.SMBus(1)

	# Load calibration parameters
	calibration_params = bme280.load_calibration_params(bus, address)
	
	try:
		# Read sensor data
		data = bme280.sample(bus, address, calibration_params)

		# Extract temperature, pressure, and humidity
		envTemp = data.temperature
		envPress = data.pressure
		envHumi = data.humidity
	
		return envTemp, envPress, envHumi
	
	except Exception as e:
		print('An unexpected error occurred while fetching the BME280 parameters:', str(e))
		return None, None, None

#Read pressure via labjack
def read_pressure(device_type="ANY", connection_type="ANY", identifier="ANY"): 
	
	#Config of labjack device
	com_config = {
		"device_type":"ANY",
		"connection_type":"ANY",
		"identifier":"ANY",
	}

	#Connect to labjack
	try:
		labjack_aging = LabJack(com_config)
		labjack_aging.start()
	
		#AIN2 as input
		pressInput = 2
		
		press = labjack_aging.get_ain(pressInput)
			
		print("Press: %f V"% press)
				
		#Convert to usable values
		#Pressure sensor: 4-20 mA sensor from 0 to 2500 mbar absolute pressure connected to a labjack probe to convert current into voltage
		#4 mA = 0 mbar -> 0.47 V
		#20 mA = 2500 mbar -> 2.36 V
		#Linear relationship p = m_{press}*V + q_{press}
		
		mpress = 1322.7513
		qpress = -621.693
		pressure = mpress*press + qpress
		
		return press, pressure
	
	except  (ConnectionRefusedError, OSError) as e:
		print("Connection error to the labjack:", {e})
		return None, None

#Read temperature and humidity via ethernet
def read_temperature_and_humidity(ip="192.168.0.7",port=1111):
	
	#Open connection to the RS232-ethernet converter
	try:
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.settimeout(15)
			s.connect((ip,port))
			data = s.recv(1024)
			
	except (socket.timeout, ConnectionRefusedError, OSError) as e:
		print("Connection error:", {e})
		return None, None
		
	#Decode message
	try:
		decoded = data.decode()
		match = re.search(r'RH\s*=\s*([-\d.]+)\s*%,\s*T\s*=\s*([-\d.]+)\s*degC',decoded)
		
		if match:
			humidity = float(match.group(1))
			temperature = float(match.group(2))
			return humidity, temperature
		else:
			print("Data format not recognized")
			return None, None
	except Exception as e:
		printf("Decoding parsing error: {e}")

#Main logger
def main():
	
	#Global variables
	debug = False
	counter = 0
	
	#db connection parameters
	secrets = dotenv_values("/home/ecoaging/logger/.env")
	
	#Connect to db
	mydb = mysql.connector.connect(
		host = secrets["host"],
		user = secrets["user"],
		password = secrets["password"],
		database = secrets["database"]
	)
	mycursor = mydb.cursor()

	#Get current timestamp
	now = datetime.now()
	print("Current date and time:", now.strftime("%Y-%m-%d %H:%M:%S"))
	
	#Get pressure from labjack
	voltagePress, pressure = read_pressure() #voltage reading, mbar reding
				
	#Get temperature and humidity from Vaisala sensor inside vessel
	humidity, temperature = read_temperature_and_humidity()
	
	#Get env temperature, pressure and humidity from BME280 outside vessel
	envTemp, envPress, envHumi = readEnv()
	
	#Printout for debug
	if temperature is not None and pressure is not None and humidity is not None:
		print("Temperature: %f C" % temperature)
		print("Pressure: %f mbar" % pressure)
		print("Voltage pressure: %f V" % voltagePress)
		print("Humidity: %f %%" % humidity)
	
	if envTemp is not None and envPress is not None and envHumi is not None:
		print("Env temperature: %f C" % envTemp)
		print("Env pressure: %f mbar" % envPress)
		print("Env humidity: %f %%" % envHumi)
	
	#Env par inside the box
	#Strange values of pressure (< 0) or temp/humi is None due to some communication issues with the RS232
	if pressure < 0 or temperature is None or humidity is None:
		print("Error while parsing vessel conditions, not uploading to db")
		counter = counter+1
		
	else:
		#MySQL query
		print("Uploading to db")
		val = (temperature,humidity,pressure,voltagePress)
		query = "INSERT INTO envPar (temperature,humidity,pressure,voltagePress) VALUES (%s,%s,%s,%s)"
		
		mycursor.execute(query,val)
		mydb.commit()
		
	#Env par in the environment
	if envTemp is None or envHumi is None or envPress is None:
		print("Error while parsing the environmental conditions, not uploading to db")
		
	else:
		#MySQL query
		print("Uploading to db")
		val = (envTemp,envPress,envHumi)
		query = "INSERT INTO environment (envTemp,envPress,envHumi) VALUES (%s,%s,%s)"
		
		mycursor.execute(query,val)
		mydb.commit()
		
		
if __name__ == "__main__":
	main()
