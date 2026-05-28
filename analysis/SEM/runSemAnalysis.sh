#!/bin/bash

slab="S12"                    #Slab name
sample="B0"                  #Sample name
area="1"                     #Area of the sample  
#type="Full Are"              #type of area
#type="EDS Spot"              #type of area
type="Selected Area"         #type of area


python3 SEM.py "~/marieCurie/EcoRPCchem/data/bakelite/${slab}/${slab}_${sample}/csv_spectra_${slab}_${sample}/Area ${area} 10 kV/${type} 1_1.csv" 1
python3 SEM.py "~/marieCurie/EcoRPCchem/data/bakelite/${slab}/${slab}_${sample}/csv_spectra_${slab}_${sample}/Area ${area} 10 kV/${type} 2_1.csv" 1
python3 SEM.py "~/marieCurie/EcoRPCchem/data/bakelite/${slab}/${slab}_${sample}/csv_spectra_${slab}_${sample}/Area ${area} 10 kV/${type} 3_1.csv" 1
python3 SEM.py "~/marieCurie/EcoRPCchem/data/bakelite/${slab}/${slab}_${sample}/csv_spectra_${slab}_${sample}/Area ${area} 10 kV/${type} 4_1.csv" 1
python3 SEM.py "~/marieCurie/EcoRPCchem/data/bakelite/${slab}/${slab}_${sample}/csv_spectra_${slab}_${sample}/Area ${area} 10 kV/${type} 5_1.csv" 1
python3 SEM.py "~/marieCurie/EcoRPCchem/data/bakelite/${slab}/${slab}_${sample}/csv_spectra_${slab}_${sample}/Area ${area} 10 kV/${type} 6_1.csv" 1
python3 SEM.py "~/marieCurie/EcoRPCchem/data/bakelite/${slab}/${slab}_${sample}/csv_spectra_${slab}_${sample}/Area ${area} 10 kV/${type} 7_1.csv" 1
python3 SEM.py "~/marieCurie/EcoRPCchem/data/bakelite/${slab}/${slab}_${sample}/csv_spectra_${slab}_${sample}/Area ${area} 10 kV/${type} 8_1.csv" 1
python3 SEM.py "~/marieCurie/EcoRPCchem/data/bakelite/${slab}/${slab}_${sample}/csv_spectra_${slab}_${sample}/Area ${area} 10 kV/${type} 9_1.csv" 1