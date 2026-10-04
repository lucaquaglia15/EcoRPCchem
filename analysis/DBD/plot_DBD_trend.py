import json
import matplotlib.pyplot as plt

def main():

    #Path to files
    #30/09/2026 -> Dry air + glass (2 mm) + single barrier discharge, wrong avg settings on the scope
    #when triggering on "single" -> the average was calculated on the single trigger hence it was the same 
    #as the "pure" channel data
    #data = "/Users/Luca/marieCurie/EcoRPCchem/data/DBD setup/dry_air_30_09_single_barrier_glass/"
    #01/10/2026 -> Dry air + glass (2 mm) + single barrier discharge
    #data = "/Users/Luca/marieCurie/EcoRPCchem/data/DBD setup/dry_air_01_10_single_barrier_glass/"
    #02/10/2026 -> Dry air + glass (2 mm) + single barrier discharge
    data = "/Users/Luca/marieCurie/EcoRPCchem/data/DBD setup/dry_air_02_10_single_barrier_glass/"

    #Values will be taken from output .json file
    voltages = []
    areas = []
    cap_m1 = [] #first slope
    cap_m2 = [] #second slope
    cap_m3 = [] #third slope
    cap_m4 = [] #fourt slope

    # Opening JSON file
    with open(data+'output.json') as f:
        outputData = json.load(f)

    #key   = string with voltage (+ some other values which will be stripped out)
    #value = dictionary with all the parameter for the given voltage value
    for voltage, parameter in outputData.items():
        #Append voltages
        volt, sep, tail = voltage.partition('-')
        voltages.append(float(str(volt)))

        #Extract other parameters, such as the area, slopes and everything else
        for par,value in parameter.items():
            m1 = value["m1"]
            cap_m1.append(m1)
            m2 = value["m2"]
            cap_m2.append(m2)
            m3 = value["m3"]
            cap_m3.append(m3)
            m4 = value["m4"]
            cap_m4.append(m4)

            #area is in microJ -> divide by 1000 to get mJ
            area = value["area"]
            areas.append(float(area)/1000.)

    #Plot energy vs peak-to-peak voltage
    fig, ax = plt.subplots()
    ax.plot(voltages, areas,"o",color="black",label="Q-V plot area vs voltage")
    ax.set_xlabel('Peak-to-peak voltage [V]')
    ax.set_ylabel('Energy [mJ]')

    #Plot slopes vs peak-to-peak voltage
    fig, ax = plt.subplots()
    ax.plot(voltages, cap_m1,"o",color="green",label="Slope m1")
    ax.plot(voltages, cap_m2,"o",color="red",label="Slope m2")
    ax.plot(voltages, cap_m3,"o",color="blue",label="Slope m3")
    ax.plot(voltages, cap_m4,"o",color="black",label="Slope m4")
    ax.set_xlabel('Peak-to-peak voltage [V]')
    ax.set_ylabel('Slopes')
    ax.legend()

    plt.show()

if __name__ == "__main__":
    main()