import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from peakutils import indexes
from peakutils import baseline
from scipy.signal import find_peaks as fp
from scipy.signal import savgol_filter
from scipy.signal import peak_widths
from scipy import sparse
from scipy.sparse.linalg import spsolve
from pathlib import Path

#Integrate valid elements
def integrate_elements(element_map_full, spectrum):
    import numpy as np

    element_integrals = {}

    for el, shells in element_map_full.items():
        total_area = 0.0

        for peak in shells["K"] + shells["L"]:
            bounds = peak["bounds"]
            # use first and last element as integration limits
            lo, hi = int(bounds[0]), int(bounds[-1])

            # clamp to spectrum
            lo = max(0, lo)
            hi = min(len(spectrum) - 1, hi)

            total_area += np.trapezoid(spectrum[lo:hi])

        element_integrals[el] = total_area

    return element_integrals

#Attach more info to a peak
def peak_info(i, peakValues, bounds):
    return {
        "peak_idx": i,
        "energy": peakValues[i],
        "bounds": bounds[i]
    }

#Enrich element map info
def attach_peak_metadata(element_map, peakValues, bounds):
    enriched = {}

    for el, shells in element_map.items():
        enriched[el] = {"K": [], "L": []}

        for shell in ("K", "L"):
            for i in shells[shell]:
                enriched[el][shell].append(
                    peak_info(i, peakValues, bounds)
                )

    return enriched

#Only get valid emission lines from the spectrum (to filter out spurious peaks)
def valid_emission_lines(elements, peaks, tol=20):
    valid_lines = set()

    for lines in elements.values():
        K, L = split_K_L(lines)

        K_found = any(peak_present(e, peaks, tol) for e in K)
        L_found = any(peak_present(e, peaks, tol) for e in L)

        if L_found and not K_found:
            continue  # reject element

        valid_lines.update(K)
        valid_lines.update(L)

    return valid_lines

#Remove the spurious peaks
def filter_spurious_peaks(peakList, peakValues, bounds, valid_lines, tol=20):
    new_peakList = []
    new_peakValues = []
    new_bounds = []

    for idx, val, bnd in zip(peakList, peakValues, bounds):
        if any(abs(val - e) <= tol for e in valid_lines):
            new_peakList.append(idx)
            new_peakValues.append(val)
            new_bounds.append(bnd)

    return new_peakList, new_peakValues, new_bounds

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

#Peak value to index
def match_peak_indices(peaks, lines, tol=20):
    return [
        i for i, p in enumerate(peaks)
        if any(abs(p - e) <= tol for e in lines)
    ]

#Element peak indeces
def element_peak_indices(lines, peaks, tol=20):
    K, L = split_K_L(lines)

    K_idx = match_peak_indices(peaks, K, tol)
    L_idx = match_peak_indices(peaks, L, tol)

    # Enforce physics:
    # L lines alone are not allowed
    if L_idx and not K_idx:
        return None

    # Element is present if at least one K or L peak exists
    if K_idx or L_idx:
        return {
            "K": sorted(K_idx),
            "L": sorted(L_idx)
        }

    return None

#Build element map
def build_element_peak_map(elements, peaks, tol=20):
    element_map = {}

    for el, lines in elements.items():
        res = element_peak_indices(lines, peaks, tol)
        if res is not None:
            element_map[el] = res

    return element_map

#Is peak present? With 20 eV tolerance
def peak_present(line_energy, peaks, tol=20):
    return any(abs(p - line_energy) <= tol for p in peaks)

#Find of the given element is present in the spectrum
#lines = emission energies in elements dictionary
#peaks = energy of the peaks found in data
#tol = tolerance of 20 eV (arbitrary)
def element_present(lines, peaks, tol=20):
    K, L = split_K_L(lines) #Split the K and L emission lines of each element in the dictionary fo all elements

    #Find peaks in our spectra that correspond to known emission lines
    K_matches = [peak for peak in peaks if any(abs(peak - line) <= tol for line in K)]
    L_matches = [peak for peak in peaks if any(abs(peak - line) <= tol for line in L)]
    
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
    
    #L_found = any(peak_present(e, peaks, tol) for e in L) #Is any of the L emission lines found in the spectrum?
    #K_found = any(peak_present(e, peaks, tol) for e in K) #Is any of the K emission lines found in the spectrum?

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
    #pathEmission = "/Users/luca/marieCurie/EcoRPCchem/data/xRayEmissions.txt"
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

    #############################
    # Load spectra from samples #
    #############################

    #Path to spectrum csv file to draw histo
    #path = Path("~/marieCurie/EcoRPCchem/data/glass/S1/S1_G1/csv_spectra_S1_G1/Area 1/Full Area 1_1.csv").expanduser()
    #path = Path("~/marieCurie/EcoRPCchem/data/bakelite/S8/S8_B1/csv_spectra_S8_B1/Area 1 10 kV/Full Area 1_1.csv").expanduser()
    #path = Path("~/marieCurie/EcoRPCchem/data/bakelite/S11/S11_B1_CS/csv_spectra_S11_B1_CS/Area 1/Selected Area 2_1.csv").expanduser()
    path = Path("~/marieCurie/EcoRPCchem/data/glass/S1/S1_G1/csv_spectra_S1_G1/Area 4_30kV/Full Area 1_1.csv").expanduser()
    #path = Path("~/marieCurie/EcoRPCchem/data/bakelite/S4/S4_B1/csv_spectra_S4_B1/Area 2/Full Area 1_1.csv").expanduser()
    #path = Path("~/marieCurie/EcoRPCchem/data/bakelite/S12/S12_B0/csv_spectra_S12_B0/Area 1 10 kV/Selected Area 4_1.csv").expanduser()
    #path = Path("~/marieCurie/EcoRPCchem/data/bakelite/S12/S12_B0/csv_spectra_S12_B0/Area 1 10 kV/Full Area 1_1.csv").expanduser()
    #path = Path("~/marieCurie/EcoRPCchem/data/bakelite/S7/S7_B0/csv_spectra_S7_B0/Area 1/EDS Spot 1_1.csv").expanduser()

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
    print("peakList:",peakList)

    #Find minima, needed for peak integration. Cannot use the built-in left/right bases since they are calculated using the peak prominence and
    #they do not correspond exactly to what we need for peak integration
    y=cleanSpectrum
    minList, _ = fp(-y) #invert the spectrum to find minima
    bounds = findMinMax(peakList, minList) #Get peak bounds from function
    print("bounds:",bounds)

    #Energy values of peaks (in eV)
    peakValues = []

    #Append the energies of the peaks to the list (we start from indeces and move to energy values in this step)
    for peak in peakList:
        val = spectrum.index[peak]*1e3
        peakValues.append(val)
        print("values:",val, val - 20, val + 20)

    ##################
    # Identify peaks #
    ##################
    elements_present = {}
    elements_rejected = {}

    #Go through the dictionary of the emission lines and check if the peaks in the data are within +- 20 eV (resolution of the EDX detector is 125 eV)
    for el, lines in emissionDict.items():
        print("el:",el)
        print("lines:",lines)

        K_matches, L_matches, present = element_present(lines, peakValues, tol=20)
        print("K matches in main:",K_matches)
        print("L matches in main:",L_matches)
        
        print("present:",present)

        if present:
            elements_present[el] = lines
        else:
            elements_rejected[el] = lines

    print("Present elements:",elements_present)

    #Debug printout
    if False:
        print("Present elements:")
        for el in elements_present:
            print(el)

        print("\nRejected (L without K):")
        for el in elements_rejected:
            print(el)

    #Build a dictionary of elements and lines in the peaks I found
    #key = element name
    #element = list of K = [a,b,c] and L = [d,e,f] where a,...,f are the indeces of the elements in my list
    element_peaks = build_element_peak_map(emissionDict,peakValues,tol=20)

    print("element_peaks:",element_peaks)
   
    #############################
    # Remove "artificial" peaks #
    #############################
    validLines = valid_emission_lines(emissionDict,peakValues,tol=20)
    validPeakindices, validPeaks, validBounds = filter_spurious_peaks(peakList, peakValues, bounds, validLines, tol=20)
    
    print("Peaks before cleaning:",peakValues)
    print("Indices before cleaning",peakList)
    print("Bounds before cleaning",bounds)
    
    print("Peaks after cleaning:",validPeaks)
    print("Indeces after cleaning",validPeakindices)
    print("Bounds after cleaning",validBounds)

    #Attach all info to element map: peak position, K and L lines, bounds of each peak
    element_map_full = attach_peak_metadata(
        element_peaks,
        peakValues, #validPeaks
        bounds #validBounds
    )

    print("\nFull elements dictionary",element_map_full,"\n")

    ###################
    # Integrate peaks #
    ###################
    totArea = 0.
    concentrations = dict()
    
    totArea = integrate_elements(element_map_full,cleanSpectrum)
    print("Integral per element:",totArea)

    #Sum all areas
    res = sum(totArea.values())
    
    #Compute concentration
    for el,area in totArea.items():
        concentrations[el] = ((area/res)*100)
        
    print("Concentrations",concentrations)

    # Create a single figure and axis
    fig, ax = plt.subplots()

    # Plot all on the same axis
    #spectrum.plot(ax=ax, label='Spot 1')

    #Draw raw spectrum
    spectrum.plot(color="blue",alpha=0.2,label="EDX spot")
    
    #Draw with Sav-Gol filter
    plt.plot(spectrum.index.to_numpy(), np.asarray(yFilter),color="green",label="Sav-Gol filter")
    #Draw baseline
    plt.plot(spectrum.index.to_numpy(), np.asarray(bl),color="pink",alpha = 0.4,label="Baseline")
    #Plot data - baseline
    plt.plot(spectrum.index.to_numpy(), np.asarray(yFilter - bl),color="grey",label="Cleaned spectrum")
    
    #Create df from cleaned data in order to plot the markers of the peaks on the cleaned spectrum
    clean_df = pd.DataFrame({"Energy": spectrum.index.values,"Counts": cleanSpectrum})

    print("\n",clean_df.iloc[validPeakindices].Counts,"\n")

    #Show peaks
    sns.scatterplot(data=clean_df.iloc[validPeakindices].reset_index(),
                    x = "Energy",
                    y = "Counts",
                    color = "red",
                    label="Peaks")
    
    #plt.legend()
    ax.legend(["Spot 1", "Spot 2", "Spot 3"])
    ax.set_xlabel("Energy [keV]")
    ax.set_ylabel("Counts")
    plt.xlim(0, 10)
    plt.grid(True)
    ax.grid(True,which="both",linewidth=0.3,alpha=0.5)

    #element_map_full is a dictionary of dictionaries
    #each dictionary has two keys, K and L representing the emission lines as lists
    #each of this lists only has one element and it is itself a dictionary and the key 'energy' has the information on the x position of the peak 
    elementNames = element_map_full.keys()

    for element in elementNames:
        lines = element_map_full[element].keys()
        for line in lines:
            if len(element_map_full[element][line])!= 0:
                plt.text((element_map_full[element][line][0]['energy'])/1000, 2500, str(element))
    
    save = False
    if save:
        plt.savefig("../../plots/S6_B1_area2_Spots.png",bbox_inches='tight',dpi=300)
    
    plt.show()

if __name__ == "__main__":
    main()