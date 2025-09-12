import subprocess
import datetime
import os
from dotenv import dotenv_values
from datetime import datetime

def main():
    
    #Get current date and time for logging
    now = datetime.now()
    print("Current date and time:", now.strftime("%Y-%m-%d %H:%M:%S"))

    #db connection parameters
    secrets = dotenv_values("/home/ecoaging/logger/.env")
    
    db_user = secrets["user"]
    db_pass = secrets["password"]
    db_name = secrets["database"]
    
    backup_dir = "/mnt/polybox/ecoagingDBbackup"

    # Ensure backup directory exists
    os.makedirs(backup_dir, exist_ok=True)

    # Always use the same filename so it overwrites the previous dump
    backup_file = os.path.join(backup_dir, "ecoagingBackup.sql")

    # Run mysqldump
    cmd = [
        "mysqldump",
        f"-u{db_user}",
        f"-p{db_pass}",
        db_name
    ]

    with open(backup_file, "w") as f:
        subprocess.run(cmd, stdout=f, check=True)

    print(f"Backup saved to {backup_file}")

if __name__ == "__main__":
	main()