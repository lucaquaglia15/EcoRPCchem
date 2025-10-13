import time
from datetime import datetime
from labjack import ljm
from hvl_ccb.dev.labjack import LabJack

#Main logger
def main():
	
	#Global variables
	debug = False
	counter = 0

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

	except  (ConnectionRefusedError, OSError) as e:
		print("Connection error to the labjack:", {e})
		return

	pressInput = 2

	while True:
		
		voltagePress = labjack_aging.get_ain(pressInput)
						
		#Convert to usable values
		#Pressure sensor: 4-20 mA sensor from 0 to 2500 mbar absolute pressure connected to a labjack probe to convert current into voltage
		#4 mA = 0 mbar -> 0.47 V
		#20 mA = 2500 mbar -> 2.36 V
		#Linear relationship p = m_{press}*V + q_{press}
			
		mpress = 1322.7513
		qpress = -621.693
		pressure = mpress*voltagePress + qpress

		#Get current timestamp
		now = datetime.now()
		print("Current date and time:", now.strftime("%Y-%m-%d %H:%M:%S"))
		
		#Printout for debug
		print("Voltage pressure: %f V" % voltagePress)
		print("Pressure %f mbar" % pressure)
		
		time.sleep(1)
		
if __name__ == "__main__":
	main()
