import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
#To find vertices of quadrilateral
from quadrilateral_fitter import QuadrilateralFitter
import os
from pathlib import Path
import sys
import json

def open_files(dataPath):

    print("path in function to open data",dataPath)
    df = pd.read_csv(dataPath, delimiter = ',',index_col=0,skiprows=5)
    df.columns = ["Amplitude"]
    df.index.names = ["Time"]

    return df

#Calculate area inside the parallelogram
def polygon_area(vertices):
    x = vertices[:, 0]
    y = vertices[:, 1]

    return 0.5 * abs(
        np.dot(x, np.roll(y, -1))
        - np.dot(y, np.roll(x, -1))
    )

#Compute intersection between lines
def line_intersection(line1, line2):
    m1, b1 = line1[:2]
    m2, b2 = line2[:2]

    x = (b2 - b1) / (m1 - m2)
    y = m1 * x + b1

    return np.array([x, y])

#Fit each side of the QV plot
def fit_side(x, y, p1, p2, tolerance):
    x1, y1 = p1
    x2, y2 = p2

    dx = x2 - x1
    dy = y2 - y1

    length = np.sqrt(dx**2 + dy**2)

    # Unit vector along the side
    ux = dx / length
    uy = dy / length

    # Vector from p1 to every experimental point
    px = x - x1
    py = y - y1

    # Position of each point along the side
    projection = px * ux + py * uy

    # Perpendicular distance from the line
    distance = np.abs(px * uy - py * ux)

    # Only keep points close to the side AND between its endpoints
    mask = (
        (distance <= tolerance) &
        (projection >= 0) &
        (projection <= length)
    )

    x_selected = x[mask]
    y_selected = y[mask]

    # Linear regression
    m, b = np.polyfit(x_selected, y_selected, 1)

    return m, b, mask

#Body of the code
def main():

    baseDebug = True

    #Startup
    print("DBD setup characterization starting!")

    #Scope channels: C1 = HV probe, C2 = capacitor, F1 = avg of C1, F2 = avg of C2
    channels = ["C1","C2","F1","F2"]

    #gases used (to build path)
    gas = "air"

    #Path to files
    #30/09/2026 -> Dry air + glass (2 mm) + single barrier discharge, wrong avg settings on the scope
    #when triggering on "single" -> the average was calculated on the single trigger hence it was the same 
    #as the "pure" channel data
    #data = "/Users/Luca/marieCurie/EcoRPCchem/data/DBD setup/dry_air_30_09_single_barrier_glass/"
    #01/10/2026 -> Dry air + glass (2 mm) + single barrier discharge
    #data = "/Users/Luca/marieCurie/EcoRPCchem/data/DBD setup/dry_air_01_10_single_barrier_glass/"
    #02/10/2026 -> Dry air + glass (2 mm) + single barrier discharge
    data = "/Users/Luca/marieCurie/EcoRPCchem/data/DBD setup/dry_air_02_10_single_barrier_glass/"
    
    #Open voltages file and save to a list
    print("Opening voltages file")
    voltagePath = data + "voltages.txt"

    #Output dictionary
    outputDict = {}

    #list for voltages
    voltages = []
    with open(voltagePath, 'r') as voltageValues:
        voltageValues.readline()
        for voltage in voltageValues:
            voltage = voltage.replace("\n", "") #Remove trailing \n
            voltages.append(voltage)

    #Loop through all voltages tested and build dataPath
    #List of df to store the time-amplitude dfs for each channel
    #dfList = [C1,C2,F1,F2]
    dfList = []

    for volt in voltages:
        for i in range(3):
            for ch in channels:
                #Build file name by looping through N numbers (N is arbitrary)
                #If the file is found, it is opened and saved to df, otherwise we break the loop
                dataPath = ""
                name = ""

                if "down" in volt:
                    dataPath = data + ch + "-" + volt.replace("-down","") + "-" + gas + "-down-" + "0000" + str(i) + ".csv"
                    print("Before",dataPath)
                    name = volt.replace("-down","") + "-" + gas + "-down-" + "0000" + str(i)
                else:
                    dataPath = data + ch + "-" + volt + "-" + gas + "-" + "0000" + str(i) + ".csv"
                    name = volt + "-" + gas + "-" + "0000" + str(i)
                
                try:
                    df = pd.read_csv(dataPath, delimiter = ',',index_col=0,skiprows=5)
                    df.columns = ["Amplitude"]
                    df.index.names = ["Time"]
                    #Append to df list only if df does not throw error (i.e. if the file exists)
                    dfList.append(df)
                    #Print (sanity check) only if df does not throw error (i.e. if the file exists)
                    print("After",dataPath)
                except:
                    break

            #Recall that dfList = [C1,C2,F1,F2]
            print("size during work:",len(dfList))

            #If there is at least one element -> we work on the data
            if (len(dfList) > 0):
                #Add element name to dictionary
                outputDict[name] = {}

                C1 = dfList[0]
                C2 = dfList[1]
                C2["Amplitude"] = C2["Amplitude"]/10.
                F1 = dfList[2]
                F2 = dfList[3]
                F2["Amplitude"] = F2["Amplitude"]/10.

                #print("C1:",C1)

                #Create quadrilateral to find vertices
                x = F1["Amplitude"].to_numpy()
                y = F2["Amplitude"].to_numpy()
                points = np.column_stack((x, y))
                #Create quadrilateral that matches the points
                fitter = QuadrilateralFitter(polygon=points)
                quadrilateral = np.array(fitter.fit())

                #Extract sides for linear fit
                tolerance = 0.02
                fits = []
                vertices = []

                try:
                    #Loop on all four sides of the parallelogram
                    for i in range(4):
                        p1 = quadrilateral[i]
                        p2 = quadrilateral[(i + 1) % 4]
                
                        m, b, mask = fit_side(x,y,p1,p2,tolerance)
                
                        fits.append((m, b, mask))
                
                        print(
                            f"Side {i+1}: "
                            f"slope = {m:.6g}, "
                            f"intercept = {b:.6g}, "
                            f"N = {mask.sum()}"
                        )

                    #Calculate area. First we need the "vertices" i.e. intersection between the four linear fits 
                    #and then we apply the function to calculate area
                    for i in range(4):
                        line1 = fits[i]
                        line2 = fits[(i + 1) % 4]
                
                        vertex = line_intersection(line1, line2)
                        vertices.append(vertex)
                
                    vertices = np.array(vertices)
                    print("vertices",vertices)
                    area = polygon_area(vertices)
                    print("Area =", area)  

                    outputDict[name]["parameters"] = {
                        "x1": vertices[0][0],
                        "y1": vertices[0][1],
                        "x2": vertices[1][0],
                        "y2": vertices[1][1],
                        "x3": vertices[2][0],
                        "y3": vertices[2][1],
                        "x4": vertices[3][0],
                        "y4": vertices[3][1],
                        "m1":fits[0][0],
                        "m2":fits[1][0],
                        "m3":fits[2][0],
                        "m4":fits[3][0],
                        "area": area}
                    
                except:
                    print("Fit or something else failed")
                    outputDict[name]["parameters"] = {
                    "x1":0,
                    "y1":0,
                    "x2":0,
                    "y2":0,
                    "x3":0,
                    "y3":0,
                    "x4":0,
                    "y4":0,
                    "m1":0,
                    "m2":0,
                    "m3":0,
                    "m4":0,
                    "area":0}

                #Clear list at the end
                dfList.clear()
                fits.clear()
                vertices = []
                points = []
                print("size at the end:",len(dfList), len(fits),len(vertices))

    print(outputDict)

    with open(data + "output.json", "w") as fp:
        json.dump(outputDict, fp, indent=4)
    
if __name__ == "__main__":
    main()