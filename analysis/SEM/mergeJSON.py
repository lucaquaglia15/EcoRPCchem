#File to merge all .json outputs from all the spots/areas in a gieven sample and area into a global json file

import json
from pathlib import Path
import os

def main():

    path = Path("~/marieCurie/EcoRPCchem/data/bakelite/S1/S1_B3/csv_spectra_S1_B3/Area 3/").expanduser() #input file path

    ext = ("1.json") #extension of files (not simply .json to avoid picking up also the global json file in the merge)

    #Extract sample name and region to save image and open .json file to write out elemental concentrations
    parts = path.parts

    for i, part in enumerate(parts):
        if part.startswith("csv_spectra_"):
            #Remove prefix "csv_spectra_"
            first = part.replace("csv_spectra_", "")
        
            #Build the rest of the path without .csv
            rest = Path(*parts[i+1:]).with_suffix("")
        
            sampleName = Path(first) / rest
            break

    sampleName = str(sampleName)
    sampleName = sampleName.replace("/","_")
    outFile = str(path) + "/" + sampleName + ".json" #Global output file

    #check if global json file exists, if yes remove it
    if os.path.isfile(outFile):
        os.remove(outFile)
    else:
        print("Gloabl merge file not found, continuing")

    outDict = [] #Gloabl dictionary for all areas

    #Loop on all files in the directory and open json of each area/spot
    for files in os.listdir(path): 
        if files.endswith(ext):
            #New dictionary to distinguish the different areas in the sample
            sample = {"sample":files}

            with open(str(path) + "/" + files) as f:
                conc = json.load(f)
                conc.update(sample)
                outDict.append(conc)
        else:
            continue
        
    with open(outFile,"w") as out:
        json.dump(outDict,out,indent=4)

if __name__ == "__main__":
    main()