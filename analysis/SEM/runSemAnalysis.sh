#!/bin/bash

slab="S1"   #Slab name
sample="B3" #Sample name
area="4"    #Area of the sample  

python3 SEM.py "~/marieCurie/EcoRPCchem/data/bakelite/${slab}/${slab}_${area}/csv_spectra_${slab}_${sample}/Area ${area}/EDS Spot 1_1.csv" 1
python3 SEM.py "~/marieCurie/EcoRPCchem/data/bakelite/${slab}/${slab}_${area}/csv_spectra_${slab}_${sample}/Area ${area}/EDS Spot 2_1.csv" 1
python3 SEM.py "~/marieCurie/EcoRPCchem/data/bakelite/${slab}/${slab}_${area}/csv_spectra_${slab}_${sample}/Area ${area}/EDS Spot 3_1.csv" 1
python3 SEM.py "~/marieCurie/EcoRPCchem/data/bakelite/${slab}/${slab}_${area}/csv_spectra_${slab}_${sample}/Area ${area}/EDS Spot 4_1.csv" 1