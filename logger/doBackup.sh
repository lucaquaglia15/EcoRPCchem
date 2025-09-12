#!/bin/bash
set -e

# Mount Polybox if not mounted
if ! mountpoint -q /mnt/polybox; then
    mount /mnt/polybox || {
        echo "Could not mount Polybox. Exiting."
        exit 1
    }
fi

mount 

# Run Python backup script
python3 /home/ecoaging/logger/backupDB.py