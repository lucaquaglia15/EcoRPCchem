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

#To do 25/01/2026
#1
#Verify that it works for all data samples

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

            total_area += np.trapz(spectrum[lo:hi])

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
    if len(lines) < 2:
        return lines, []

    split_idx = None
    for i in range(1, len(lines)):
        if (lines[i] + 50) < lines[i - 1]:
            split_idx = i
            break

    if split_idx is None:
        # Only K lines
        return lines, []

    K = lines[:split_idx]
    L = lines[split_idx:]
    return K, L

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

#There is L line but no K line
def element_present(lines, peaks, tol=20):
    K, L = split_K_L(lines)
    #print("K",K)
    #print("L",L)

    L_found = any(peak_present(e, peaks, tol) for e in L)
    K_found = any(peak_present(e, peaks, tol) for e in K)

    if L_found and not K_found:
        return False   # physically inconsistent
    elif not L_found and not K_found:
        return False 
    
    return L_found or K_found

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
    pathEmission = "/home/luca/cernbox/marieCurie/EcoRPCchem/data/xRayEmissions.txt"

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
    #path = "/home/luca/cernbox/marieCurie/EcoRPCchem/data/glass/S1/S1_G1/csv_spectra_S1_G1/Area 1/Full Area 1_1.csv"
    #path = "/home/luca/cernbox/marieCurie/EcoRPCchem/data/bakelite/S8/S8_B1/csv_spectra_S8_B1/Area 1 10 kV/Full Area 1_1.csv"
    path = "/home/luca/cernbox/marieCurie/EcoRPCchem/data/glass/S1/S1_G1/csv_spectra_S1_G1/Area 4_30kV/Full Area 1_1.csv"
    #path = "/home/luca/cernbox/marieCurie/EcoRPCchem/data/bakelite/S12/S12_B0/csv_spectra_S12_B0/Area 1 10 kV/Selected Area 4_1.csv"

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
    print(info)

    #Find minima, needed for peak integration. Cannot use the built-in left/right bases since they are calculated using the peak prominence and
    #they do not correspond exactly to what we need for peak integration
    y =cleanSpectrum
    minList, _ = fp(-y) #invert the spectrum to find minima
    bounds = findMinMax(peakList, minList) #Get peak bounds from function
    print(bounds)

    #Energy values of peaks (in eV)
    peakValues = []

    #Check if all elements of emission energy list for one element are present in peak list
    for peak in peakList:
        val = spectrum.index[peak]*1e3
        peakValues.append(val)
        print("values:",val, val - 20, val + 20)

    ##################
    # Identify peaks #
    ##################
    elements_present = {}
    elements_rejected = {}

    #Is the emission line present in the data?
    for el, lines in emissionDict.items():
        present = element_present(lines, peakValues, tol=20)

        if present:
            elements_present[el] = lines
        else:
            elements_rejected[el] = lines

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
    element_peaks = build_element_peak_map(
        emissionDict,
        peakValues,
        tol=20
    )

    print(element_peaks)
   
    #############################
    # Remove "artificial" peaks #
    #############################
    validLines = valid_emission_lines(emissionDict,peakValues,tol=20)
    validPeakindices, validPeaks, validBounds = filter_spurious_peaks(peakList, peakValues, bounds, validLines, tol=20)
    
    print("Peaks before cleaning:",peakValues,"indices",peakList,"bounds",bounds)
    print("Peaks after cleaning:",validPeaks,"indeces",validPeakindices,"bounds",validBounds)

    #Attach all info to element map: peak position, K and L lines, bounds of each peak
    element_map_full = attach_peak_metadata(
        element_peaks,
        validPeaks,
        validBounds
    )

    print("Full elements dictionary",element_map_full)

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

    #Draw raw spectrum
    spectrum.plot(color="blue",alpha=0.2,label="Original data")
    #Draw with Sav-Gol filter
    plt.plot(spectrum.index.to_numpy(), np.asarray(yFilter),color="green",label="Sav-Gol filter")
    #Draw baseline
    plt.plot(spectrum.index.to_numpy(), np.asarray(bl),color="pink",alpha = 0.2,label="Baseline")
    #Plot data - baseline
    plt.plot(spectrum.index.to_numpy(), np.asarray(yFilter - bl),color="grey",label="Cleaned spectrum")
    
    #Create df from cleaned data in order to plot the markers of the peaks on the cleaned spectrum
    clean_df = pd.DataFrame({"Energy": spectrum.index.values,"Counts": cleanSpectrum})

    #Show peaks
    sns.scatterplot(data=clean_df.iloc[validPeakindices].reset_index(),
                    x = "Energy",
                    y = "Counts",
                    color = "red",
                    label="Peaks")
    
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()