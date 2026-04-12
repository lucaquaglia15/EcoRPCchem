import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from scipy.signal import find_peaks as fp
from scipy.signal import savgol_filter
from scipy import sparse
from scipy.sparse.linalg import spsolve
from pathlib import Path
import sys
import json

#Integrate valid elements
def integrate_elements(element_map_full, spectrum):
    import numpy as np

    element_integrals = {}

    for el, shells in element_map_full.items():
        total_area = 0.0
        print(el, shells)

        for peak in shells["K"] + shells["L"]:
            print(peak[0],peak[2])

            lo, hi = int(peak[0]), int(peak[2])

            #Clamp to spectrum to avoid that the min and meax of each integration interval is not < 0 or > end of spectrum
            lo = max(0, lo)
            hi = min(len(spectrum) - 1, hi)

            total_area += np.trapezoid(spectrum[lo:hi])
            
        element_integrals[el] = total_area

    return element_integrals

#Split K and L lines
def split_K_L(lines):
    if len(lines) <= 3: #We only have Ka1, Ka2 and Kb1
        return lines, [] #Return only K lines and empty L

    split_idx = None #index of the list where we go from K to L lines
    
    for i in range(1, len(lines)):
        if (lines[i] + 50) < lines[i - 1]:
            split_idx = i
            break

    #In principle this is not needed since we check before if the length of the emission dictionary element is <= 3 (i.e. if there is only K lines) but ok
    #We can leave it just in case
    if split_idx is None:
        return lines, []

    #K lines is whatever is before the split idx
    #L lines is whatever is after the split idx
    K = lines[:split_idx]
    L = lines[split_idx:]
    return K, L #K and L as lists

#Find of the given element is present in the spectrum
#lines = emission energies in elements dictionary
#peaks = energy of the peaks found in data
#tol = tolerance of 20 eV (arbitrary)
#def element_present(lines, peaks, tol=20):
def element_present(lines, peakStructure, tol=20):   
    
    K, L = split_K_L(lines) #Split the K and L emission lines of each element in the dictionary fo all elements

    K_matches= [
        peak for peak in peakStructure
        if any(abs(peak[4] - line) <= tol for line in K)
    ]

    L_matches= [
        peak for peak in peakStructure
        if any(abs(peak[4] - line) <= tol for line in L)
    ]

    #print("K_matches:",K_matches)
    #print("L_matches:",L_matches)

    #Bools to understand if we find L matches without K matches
    K_found = False
    L_found = False

    #Based on the length of the matches lists
    if len(K_matches) > 0:
        K_found = True
    if len(L_matches) > 0:
        L_found = True
    
    if L_found and not K_found: #L lines are weaker than K so if we find some L lines without K it might mean that the L lines are just noise peaks
        return ([],[],False)   
    elif not L_found and not K_found: #If none is found (maybe it never happens) it is not even to be considered an element
        return ([],[],False)   
    
    #print("K_found:",K_found,"L_found:",L_found)  
    return (K_matches, L_matches, L_found or K_found)

#Find peak min and max 
def findMinMax(peaks, mins):

    bounds = []

    for p in peaks:
        left_mins  = mins[mins < p]
        right_mins = mins[mins > p]

        if len(left_mins) == 0 or len(right_mins) == 0:
            continue

        left  = left_mins[-1]
        right = right_mins[0]

        bounds.append((left, p, right))
    
    return bounds

#ALS baseline from https://stackoverflow.com/questions/29156532/python-baseline-correction-library
def baseline_als(y, lam, p, niter):
  L = len(y)
  D = sparse.diags([1,-2,1],[0,-1,-2], shape=(L,L-2))
  w = np.ones(L)
  for i in range(niter):
    W = sparse.spdiags(w, 0, L, L)
    Z = W + lam * D.dot(D.transpose())
    z = spsolve(Z, w*y)
    w = p * (y > z) + (1-p) * (y < z)
  return z

#Main function
def main():

    #If true -> debug printouts enabled
    debug = False

    ##############################
    # Load energy emission lines #
    ##############################

    #Path to x-ray emission lines table
    pathEmission = Path("~/marieCurie/EcoRPCchem/data/xRayEmissions.txt").expanduser()

    #Dictionary for x-ray emission energy lines
    emissionDict = dict()
    #List to temporarily store energy values and add them to the dictionary
    tempEn = []

    with open(pathEmission, 'r') as emissions:
        for element in emissions:
        
            element = element.replace("\n", "") #Remove trailing \n
            element = element.split("\t") #Split string in list in correspondence of \t
        
            element.pop(0) #Remove first element (number identifier of the element obtained from website: https://physics.uwo.ca/~lgonchar/courses/p9826/xdb.pdf)
            key = element[0] #Key for dictionary
        
            element.pop(0) #remove element name
           
           #Add all emission energy to a temporary list
            for temp in element:
                if temp != '—':
                    tempEn.append(float(temp))

            #Add list to dictionary, key is element name
            emissionDict[key] = tempEn.copy()

            #Clear list for next element
            tempEn.clear() 
    
    if debug:
        print(emissionDict)

    ###############################
    # Load spectra from sample(s) #
    ###############################

    #Path to spectrum csv file to draw histo
    #If executed from python script -> get the path from .sh script, otherwise hard coded here
    if len(sys.argv) < 2: #No string from command line
        #path = Path("~/marieCurie/EcoRPCchem/data/glass/S1/S1_G1/csv_spectra_S1_G1/Area 1/Full Area 1_1.csv").expanduser()
        #path = Path("~/marieCurie/EcoRPCchem/data/bakelite/S8/S8_B1/csv_spectra_S8_B1/Area 1 10 kV/Full Area 1_1.csv").expanduser()
        #path = Path("~/marieCurie/EcoRPCchem/data/bakelite/S11/S11_B1_CS/csv_spectra_S11_B1_CS/Area 1/Selected Area 2_1.csv").expanduser()
        #path = Path("~/marieCurie/EcoRPCchem/data/glass/S1/S1_G1/csv_spectra_S1_G1/Area 4_30kV/Full Area 1_1.csv").expanduser()
        #path = Path("~/marieCurie/EcoRPCchem/data/bakelite/S4/S4_B1/csv_spectra_S4_B1/Area 2/Full Area 1_1.csv").expanduser()
        #path = Path("~/marieCurie/EcoRPCchem/data/bakelite/S12/S12_B0/csv_spectra_S12_B0/Area 1 10 kV/Selected Area 4_1.csv").expanduser()
        #path = Path("~/marieCurie/EcoRPCchem/data/bakelite/S12/S12_B0/csv_spectra_S12_B0/Area 1 10 kV/Full Area 1_1.csv").expanduser()
        path = Path("~/marieCurie/EcoRPCchem/data/bakelite/S7/S7_B0/csv_spectra_S7_B0/Area 1/EDS Spot 1_1.csv").expanduser()
    
    else:
        path = Path(sys.argv[1]).expanduser()

    energy, counts = np.genfromtxt(path,delimiter=',',unpack=True)

    if debug:
        print("Energy:",energy)
        print("Counts:",counts)

    #Load spectrum to find peaks
    spectrum = pd.read_csv(path, delimiter = ',',index_col=0)
    spectrum.columns = ["Counts"]
    spectrum.index.names = ["Energy"]

    if debug:
        print(spectrum)

    ##########################
    # Sav Gol filter on data #
    ##########################
    windowLength = 15 #was 11
    polyOrder = 6 #was 5
    yFilter = savgol_filter(spectrum.Counts,window_length=windowLength,polyorder=polyOrder) 
    if debug:
        print(savgol_filter)
    
    ####################
    # Compute baseline #
    ####################
    #1e+4, 0.001 10
    bl = baseline_als(yFilter, 1e+4, 0.001, 200) 
    cleanSpectrum = yFilter - bl  

    ##################################
    # Find peaks with scipy baseline #
    ##################################
    h = 50 #Was 175 and working good
    prom = 60 #Was 75 and working good
    dist = None #Was 5 but not working as good either

    peakList, info = fp(x=cleanSpectrum,
               height=h,
               prominence=prom,
               distance=dist)
    
    print("info:",info)
    print(info['peak_heights'][0])
    print("peakList:",peakList)

    #Find minima, needed for peak integration. Cannot use the built-in left/right bases since they are calculated using the peak prominence and
    #they do not correspond exactly to what we need for peak integration
    y=cleanSpectrum
    minList, _ = fp(-y) #invert the spectrum to find minima
    bounds = findMinMax(peakList, minList) #Get peak bounds from function
    bounds = [(int(x), int(y), int(z)) for (x, y, z) in bounds]
    print("bounds:",bounds)
    
    #All peak structure in eV rather than indeces
    peakStructure = []
    
    #Convert all elements from indeces to eenrgy values
    #peak structure is: (index of left peak min, index of peak, index of right peak min, left peak min in eV, peak in eV, right peak min in eV, peak height)
    #indeces are needed for integration and peak height for plotting element names at the end
    for i,peak in enumerate(bounds):
        m1 = peak[0]
        p = peak[1]
        m2 = peak[2]
        m1En = spectrum.index[peak[0]]*1e3
        pEn = spectrum.index[peak[1]]*1e3
        m2En = spectrum.index[peak[2]]*1e3
        h = info['peak_heights'][i]

        peakTuple = (m1,p,m2,m1En,pEn,m2En,h)
        peakStructure.append(peakTuple)
    
    #This is a sanity check to check if the code can detect a fake peak and not consider it in the analysis. The values are all random and made up by me
    #extraPeak = (450,460,470,4875,4980,5090,481.63339537078315)
    #peakStructure.append(extraPeak)
    
    #convert from np.float and np.int to "normal" float and int
    peakStructure = [(int(a), int(b), int(c), float(x), float(y), float(z), float(h)) for (a, b, c, x, y, z, h) in peakStructure]
    
    print(peakStructure)

    ##################
    # Identify peaks #
    ##################
    elements_present = {}
    elements_rejected = {}
    #Final dictionary of present elements
    present_element_peaks = {}

    #Go through the dictionary of the emission lines and check if the peaks in the data are within +- 20 eV (resolution of the EDX detector is 125 eV)
    for el, lines in emissionDict.items():
        print("el:",el)
        print("lines:",lines)
       
        K_matches, L_matches, present = element_present(lines, peakStructure, tol=20)

        print("K matches in main:",K_matches)
        print("L matches in main:",L_matches)
        print("present in main:",present)

        #Build element dictionary
        if present:
            present_element_peaks[el] = {
                'K': K_matches,
                'L': L_matches
            }

        #This is not realyl necessary for analysis but only for debug it's left
        if present:
            elements_present[el] = lines
        else:
            elements_rejected[el] = lines
    
    #This is with the energy from the emission line dictionary
    if False:
        print("Present elements:",elements_present)

    print("present_element_peaks built by me",present_element_peaks)

    ###################
    # Integrate peaks #
    ###################
    totArea = 0.
    concentrations = dict()
    
    totArea = integrate_elements(present_element_peaks,cleanSpectrum)
    print("Integral per element:",totArea)

    #Sum all areas
    res = sum(totArea.values())
    
    #Compute concentration
    for el,area in totArea.items():
        concentrations[el] = ((area/res)*100)
        
    print("Concentrations",concentrations)

    #Create single plot
    ax = spectrum.plot(color="blue",alpha=0.4,label="EDX spot")
    
    #Draw with Sav-Gol filter
    plt.plot(spectrum.index.to_numpy(), np.asarray(yFilter),color="green",label="Sav-Gol filter")
    #Draw baseline
    plt.plot(spectrum.index.to_numpy(), np.asarray(bl),color="pink",alpha = 0.4,label="Baseline")
    #Plot data - baseline
    plt.plot(spectrum.index.to_numpy(), np.asarray(yFilter - bl),color="grey",label="Cleaned spectrum")
    
    #Create df from cleaned data in order to plot the markers of the peaks on the cleaned spectrum
    clean_df = pd.DataFrame({"Energy": spectrum.index.values,"Counts": cleanSpectrum})

    #Extract index of the peak and name of the element from the dictionary
    validPeakindicesNames = [
        {"idx": peak[1], "element": el}
        for el, shells in present_element_peaks.items()
        for peaks in shells.values()
        for peak in peaks
    ]

    #Convert to df
    validPeakindicesNames_df = pd.DataFrame(validPeakindicesNames)

    #Show peaks on the plot
    sns.scatterplot(
        data=clean_df.iloc[validPeakindicesNames_df["idx"]].reset_index(),
        x="Energy",
        y="Counts",
        color="red",
        label="Peaks"
    )

    #Write down element names on the plot
    for i, row in validPeakindicesNames_df.iterrows():
        idx = row["idx"]
        el = row["element"]
        
        x = clean_df.iloc[idx]["Energy"]
        y = clean_df.iloc[idx]["Counts"]
        
        plt.text(x, y+50, el, color="red", fontsize=9, ha='center', va='bottom')
    
    plt.legend()
    ax.set_xlabel("Energy [keV]")
    ax.set_ylabel("Counts")
    plt.xlim(0, 10)
    plt.grid(True)
    ax.grid(True,which="both",linewidth=0.3,alpha=0.5)

    #Extract sample name and region to save image and open .txt file to write out elemental concentrations
    parts = path.parts

    for i, part in enumerate(parts):
        if part.startswith("csv_spectra_"):
            #Remove prefix "csv_spectra_"
            first = part.replace("csv_spectra_", "")
        
            #Build the rest of the path without .csv
            rest = Path(*parts[i+1:]).with_suffix("")
        
            sampleName = Path(first) / rest
            break
    
    #Convert to string
    sampleName = str(sampleName)
    #Replace / and spaces with _
    sampleName = sampleName.replace("/","_")
    sampleName = sampleName.replace(" ","_")

    #Understand from the context if the plot needs to be saved on disk or not
    if len(sys.argv) < 3:
        save = False
    else: 
        save = bool(int(sys.argv[2]))
    
    if save:
        plt.savefig("../../plots/" + sampleName + ".png",bbox_inches='tight',dpi=300)
    
    plt.show()
    
    path = str(path).replace(".csv",".json")
    #Save element concentrations to a .json file in the csv folder of each sample
    with open(path,"w") as conc:
        json.dump(concentrations,conc)

if __name__ == "__main__":
    main()