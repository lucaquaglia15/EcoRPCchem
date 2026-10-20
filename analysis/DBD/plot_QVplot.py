import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
#To find vertices of quadrilateral
from quadrilateral_fitter import QuadrilateralFitter
from scipy.signal import butter, sosfiltfilt
import os
from pathlib import Path
import sys
import json

def open_files(dataPath,timeShift,ampShift):

    print(dataPath)

    #Open an example file and plot
    #exC1 = dataPath + "C1-20000-air-00000.csv"
    #exC2 = dataPath + "C2-20000-air-00000.csv"
    #exF1 = dataPath + "F1-20000-air-00000.csv"
    #exF2 = dataPath + "F2-20000-air-00000.csv"

    exC1 = dataPath + "C1-3500-ar-10-slm-00000.csv"
    exC2 = dataPath + "C2-3500-ar-10-slm-00000.csv"
    exF1 = dataPath + "F1-3500-ar-10-slm-00000.csv"
    exF2 = dataPath + "F2-3500-ar-10-slm-00000.csv"

    #Load waveform
    C1 = pd.read_csv(exC1, delimiter = ',',index_col=0,skiprows=5)
    C1.columns = ["Amplitude"]
    C1.index.names = ["Time"]

    C2 = pd.read_csv(exC2, delimiter = ',',index_col=0,skiprows=5)
    C2.columns = ["Amplitude"]
    C2["Amplitude"] = C2["Amplitude"]/10.
    C2.index.names = ["Time"]

    F1 = pd.read_csv(exF1, delimiter = ',',index_col=0,skiprows=5)
    F1.columns = ["Amplitude"]
    F1.index.names = ["Time"]
    
    F2 = pd.read_csv(exF2, delimiter = ',',index_col=0,skiprows=5)
    F2.columns = ["Amplitude"]
    mask = pd.to_numeric(F2["Amplitude"], errors="coerce").isna()
    print(F2.loc[mask, "Amplitude"].map(repr).head(20))
    F2['Amplitude'] = F2['Amplitude'].astype(float)
    F2["Amplitude"] = F2["Amplitude"]/10.
    F2.index.names = ["Time"]

    #Older data only 
    if ampShift and dataPath != "/Users/Luca/marieCurie/EcoRPCchem/data/DBD setup/dry_air_15_10_single_barrier_glass/":
        C1["Amplitude"] = C1["Amplitude"]+50
        F1["Amplitude"] = F1["Amplitude"]+50
    
    elif ampShift and dataPath == "/Users/Luca/marieCurie/EcoRPCchem/data/DBD setup/dry_air_15_10_single_barrier_glass/":
        C1["Amplitude"] = C1["Amplitude"]+50
        C2["Amplitude"] = C2["Amplitude"]-(0.0002941/2) #0.00044567/2
        F1["Amplitude"] = F1["Amplitude"]+50
        F2["Amplitude"] = F2["Amplitude"]-(0.0002941/2) #0.00044567/2)

    #if timeShift and dataPath != "/Users/Luca/marieCurie/EcoRPCchem/data/DBD setup/dry_air_15_10_single_barrier_glass/":
    if timeShift and dataPath != "/Users/Luca/marieCurie/EcoRPCchem/data/DBD setup/dry_air_15_10_single_barrier_glass/":
        #New values with offset correction
        C2.index = C2.index + 1.003e-05
        F2.index = F2.index + 1.003e-05

    return C1, C2, F1, F2

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

    #Path to files
    #30/09/2026 -> Dry air + glass (2 mm) + single barrier discharge, wrong avg settings on the scope
    #when triggering on "single" -> the average was calculated on the single trigger hence it was the same 
    #as the "pure" channel data
    #data = "/Users/Luca/marieCurie/EcoRPCchem/data/DBD setup/dry_air_30_09_single_barrier_glass/"
    #01/10/2026 -> Dry air + glass (2 mm) + single barrier discharge
    #data = "/Users/Luca/marieCurie/EcoRPCchem/data/DBD setup/dry_air_01_10_single_barrier_glass/"
    #02/10/2026 -> Dry air + glass (2 mm) + single barrier discharge
    #data = "/Users/Luca/marieCurie/EcoRPCchem/data/DBD setup/dry_air_02_10_single_barrier_glass/"
    #06/10/2026 -> Dry air + glass (2 mm) + single barrier discharge
    #data = "/Users/Luca/marieCurie/EcoRPCchem/data/DBD setup/dry_air_06_10_single_barrier_glass/"
    #15/10/2026 -> Dry air + glass (2 mm) + single barrier discharge -> scan with small voltage steps
    #data = "/Users/Luca/marieCurie/EcoRPCchem/data/DBD setup/dry_air_15_10_single_barrier_glass/"
    #20/10/2026 -> Dry Ar + glass (2mm) + single barrier discharge, measurements at different Ar flows and without flow
    #data = "/Users/Luca/marieCurie/EcoRPCchem/data/DBD setup/dry_Ar_2_slm_20_10_single_barries_glass/"
    #data = "/Users/Luca/marieCurie/EcoRPCchem/data/DBD setup/dry_Ar_5_slm_20_10_single_barries_glass/"
    data = "/Users/Luca/marieCurie/EcoRPCchem/data/DBD setup/dry_Ar_10_slm_20_10_single_barries_glass/"
    #data = "/Users/Luca/marieCurie/EcoRPCchem/data/DBD setup/dry_Ar_no_gas_flow_single_barrier_glass/"
    
    
    #Open files and save to df
    #data, timeShift, ampShift
    C1, C2, F1, F2 = open_files(data,True,True)

    #Reduce the data from four periods to one to see if the oscillations in the QV plot are reduced
    reduceToOnePeriod = False
    start = 0.0025
    end = 0.0051

    if reduceToOnePeriod:
        C1 = C1[(C1.index >= start) & (C1.index <= end)]
        C2 = C2[(C2.index >= start) & (C2.index <= end)]
        F1 = F1[(F1.index >= start) & (F1.index <= end)]
        F2 = F2[(F2.index >= start) & (F2.index <= end)]
    
    #QV plot with all fits
    fig, ax = plt.subplots()
    ax.plot(F1["Amplitude"], F2["Amplitude"],".",color="black",label="X-Y plot")
    ax.set_xlabel('Amplitude [V]')
    ax.set_ylabel(r'Charge [$\mu$C]')
    ax.grid(linestyle = '--', color = 'lightgrey')

    #Convert to useful format for QuadrilateralFitter library
    x = F1["Amplitude"].to_numpy()
    y = F2["Amplitude"].to_numpy()
    points = np.column_stack((x, y))

    #Create quadrilateral that matches the points
    fitter = QuadrilateralFitter(polygon=points)
    quadrilateral = np.array(fitter.fit())

    # Close the quadrilateral and plot it (if needed)
    #quad_closed = np.vstack([quadrilateral, quadrilateral[0]])
    #Plot quadrilateral
    #plt.plot(quad_closed[:, 0],quad_closed[:, 1],"-",color="red",linewidth=2,label="Fitted quadrilateral")
    #Plot four corners
    #plt.plot(quadrilateral[:, 0],quadrilateral[:, 1],"o",color="black")

    #if True:
    #    print("Quadrilateral:",quadrilateral)

    #Order the values in increasing order
    idx = np.argsort(quadrilateral[:, 0])
    quadrilateral[:] = quadrilateral[idx[[0, 2, 3, 1]]]

    if True:
        print("Quadrilateral:",quadrilateral)

    #Extract sides for linear fit
    tolerance = 0.02
    fits = []

    #Fit parallelogram sides
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

        for i, (m, b, mask) in enumerate(fits):
            p1 = quadrilateral[i]
            p2 = quadrilateral[(i + 1) % 4]

            #Plot selected points
            plt.plot(x[mask],y[mask],".",markersize=5,label=f"Side {i+1} points")

            #Plot regression line
            x_line = np.linspace(min(p1[0], p2[0]),max(p1[0], p2[0]),100)
            y_line = m * x_line + b

            plt.plot(x_line,y_line,linewidth=2,label=f"Fit {i+1}: m={m:.4g}")
        plt.legend()

        #Calculate area. First we need the "vertices" i.e. intersection between the four linear fits 
        #and then we apply the function to calculate area
        vertices = []
        for i in range(4):
            line1 = fits[i]
            line2 = fits[(i + 1) % 4]

            vertex = line_intersection(line1, line2)
            vertices.append(vertex)

        vertices = np.array(vertices)

        print("vertices",vertices)

        area = polygon_area(vertices)
        print("Area =", area)

        # Plot vertices
        plt.plot(vertices[:, 0],vertices[:, 1],"o",color="yellow",label="Fitted vertices")

    #If for any reason the quadrilateral fails -> draw whatever is produced on top of the plot and do not perform fit
    except:
        #Close the quadrilateral and plot it (if needed)
        quad_closed = np.vstack([quadrilateral, quadrilateral[0]])
        #Plot quadrilateral
        plt.plot(quad_closed[:, 0],quad_closed[:, 1],"-",color="red",linewidth=2,label="Fitted quadrilateral")
        #Plot four corners
        #plt.plot(quadrilateral[:, 0],quadrilateral[:, 1],"o",color="black")
    
    #Plot on 4 separate panels
    #Plot Q-V plot without rolling mean
    ax = C1.plot(color="blue",marker=".",alpha=0.8,label="Ex C1")
    ax.legend(["Ex C1"])
    ax.set_xlabel('Time [ms]')
    ax.set_ylabel('Peak-to-peak amplitude [V]')
    ax.grid(linestyle = '--', color = 'lightgrey')

    ax = C2.plot(color="red",alpha=0.8,label="Ex C2")
    ax.legend(["Ex C2"])
    ax.set_xlabel('Time [ms]')
    ax.set_ylabel(r'Charge [$\mu$C]')
    ax.grid(linestyle = '--', color = 'lightgrey')

    #Butterworth filter on F1
    fs = 100000 #Number of samples
    cutoff = 5000  #Cutoff frequency
    sos = butter(4,cutoff,btype="lowpass",fs=fs,output="sos")
    F1["Amp_fil"] = sosfiltfilt(sos, F1["Amplitude"])

    ax = F1.plot(color="green",alpha=0.8,label="Ex F1")
    #ax.plot(F1.index,F1['Amp_fil'],label= 'Butterworth',color="pink")
    #ax.legend(["Ex F1 (avg CH1)","Butterworth filter"])
    ax.grid(linestyle = '--', color = 'lightgrey')

    ax = F2.plot(color="orange",alpha=0.8,label="Ex F2 (avg CH2)")
    C2.plot(color="green",label="Ex C2",alpha=0.2,ax=ax)
    ax.legend(["Ex F2 (avg CH2)", "C2 (no average)"])
    ax.grid(linestyle = '--', color = 'lightgrey')

    #QV plot with not fits
    rollMeanNumber = 20000
    fig, ax = plt.subplots()
    #Old - simple F1 vs F2
    ax.plot(F1["Amplitude"], F2["Amplitude"],".",color="black",label="X-Y plot")
    #New - rolling mean
    #ax.plot(F1['Amplitude'].rolling(rollMeanNumber, center=True).mean(),F2["Amplitude"],".",color="black",label="X-Y plot")
    #New - Butterworth filter
    #ax.plot(F1['Amp_fil'],F2["Amplitude"],".",color="black",label="X-Y plot")
    ax.set_xlabel('Amplitude [V]')
    ax.set_ylabel(r'Charge [$\mu$C]')
    ax.grid(linestyle = '--', color = 'lightgrey')
    
    #F1 and F2 on the same panel
    fig, axs = plt.subplots()
    p1 = axs.plot(F1.index, F1.Amplitude, '-', label = 'Avg HV signal', c='green')
    ax1 = axs.twinx()
    p2 = ax1.plot(F2.index, F2.Amplitude, '-', label = 'Avg charge signal', c='red')
    ax1.tick_params(axis='y')
    axs.set_ylabel('Amplitude [V]')
    ax1.set_ylabel(r'Charge [$\mu$C]')
    axs.set_xlabel('Time')
    #Align y=0 on both axes by making both axes symmetric around zero
    y1 = max(abs(x) for x in axs.get_ylim())
    y2 = max(abs(x) for x in ax1.get_ylim())
    axs.set_ylim(-y1, y1)
    ax1.set_ylim(-y2, y2)
    l = p1 + p2
    labs = [li.get_label() for li in l]
    axs.legend(l, labs, loc='upper left', fontsize = 8)
    axs.grid(linestyle = '--', color = 'lightgrey')

    processCharge = True #If True -> charge and voltage across the gap are computed

    if processCharge:
        #Calculate U_{g}(t) and Q(t) -> voltage across the gas gap and charge per cycle
        #Cs = 11.57e-6 #stray capacitance (in uF) -> from calculation of C_cell_measured - C_cell_theo - C_spacers
        #Cs = 13.27e-6 #stray capacitance (in uF) including 1.7e-6 uF for the three spacers
        #Cs = 20e-6-6.03e-6-1.7e-6 #Best so far
        #Cs = 9.6e-6
        #Cd = 35.9e-6 #ideal dielectric capacitance (in uF)
        #Cd = 90e-6-12.27e-6  #dielectric capacitance from Q-V plot (in uF)
        Cs = 10.4e-6 #C_stray = C_cell_meas(19.3 pF) - 3xC_spacer_calc(1.7 pF) - C_cell_theo(7.2 pF)
        Cd = 90e-6-Cs #Dielectric capacitance from Q-V plot (in uF) - C_stray
        Ccell = 7.2e-6 #Ideal cell capacitance (in uF) from calculation only with flat part of the electrode
        
        #0.13 and 0.87 work the best
        alpha = 0
        beta = 1

        """
        if alpha+beta > 1:
            return
        elif alpha+beta < 1:
            return
        """
        # Calculate voltage and charge sample by sample
        F1_amp = F1["Amplitude"].to_numpy()
        F2_amp = F2["Amplitude"].to_numpy()
        
        #This uses the numpy array version of the amplitudes (in F1 and F2) because if you perform a time shift on the index 
        #to allign F1 and F2 at low voltages (where no phase shift is expected) and then you just combine F1["Amplitude"] and F2["Amplitude"]
        #the indexes are not aligned and then the calculation creates a pd series with double the number of entries to take into account
        #the fact that the index is not shared between F1["Amplitude"] and F2["Amplitude"]
        U_t = ((1+((alpha*Ccell + Cs)/(beta*Cd)))*F1_amp) - ((1/(beta*Cd))*F2_amp)
        q_t = (Cd/(Cd-Ccell))*(F2_amp - (Ccell+Cs)*F1_amp)

        #U_g(t) and q(t) on the same panel
        fig, axs = plt.subplots()
        p1 = axs.plot(F1.index, U_t, '-', label = 'U_g (t)', c='green')
        ax1 = axs.twinx()
        p2 = ax1.plot(F1.index, q_t, '-', label = 'q(t)', c='red')
        ax1.tick_params(axis='y')
        axs.set_ylabel(r'U$_{g}$ (t) [V]')
        ax1.set_ylabel(r'q(t) [$\mu$C]')
        axs.set_xlabel('Time')

        #Align y=0 on both axes by making both axes symmetric around zero
        y1 = max(abs(x) for x in axs.get_ylim())
        y2 = max(abs(x) for x in ax1.get_ylim())

        axs.set_ylim(-y1, y1)
        ax1.set_ylim(-y2, y2)
        
        l = p1 + p2
        labs = [li.get_label() for li in l]
        axs.legend(l, labs, loc='upper left', fontsize = 8)
        axs.grid(linestyle = '--', color = 'lightgrey')
        
        #Plot q(t) vs U_g(t)
        fig, ax = plt.subplots()
        ax.plot(U_t, q_t, '-', label = 'q(t) vs U(t)', c='green')

    #Show all plots
    plt.show()

if __name__ == "__main__":
    main()