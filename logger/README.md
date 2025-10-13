This folder contains the scripts used to log the environmental data during the material compatibility studies

All the scritps run on a Raspberry Pi which is installed in a box next to the experimental setup

1) `logger.py`: python script to read the pressure inside the vessel from the Wika P30 sensor, the RH/temperature inside the vesse from the Vaisala HMT310 sensor and the environmental temperature/pressure/RH from the BM280 sensor 

2) `runLogger.sh`: executable file which is used to run the logger script every 10 minutes via crontab

3) `backupDB.py`: python script to execute db backup on PolyBox

4) `doBackup.sh`: executable file which is used to run the backupDB.py file every night at 2 am via crontab

5) `filling.py`: short script to read the pressure in the vessel every 1 seconds for the filling process

More details about the methodology of the studies are reported on Zenodo (link will be added soon)
