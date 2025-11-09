import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

day = input("Which day do you want to visualize? (7,17,24)")
month = input("Which month? (Oct,Nov)?")
year = input("Which year? (2025)")

path = "/home/luca/cernbox/marieCurie/EcoRPCchem/data/vesselFilling_" + str(month) + "_" + str(day) + "_" + str(year) + "/"
fileName = "vessel_pressure_" + str(day) + "_" + str(month) + "_" + str(year) + ".csv"

points = [] #  empty regular list

# Load CSV
df = pd.read_csv(path+fileName, sep=None, engine="python")
df.columns = df.columns.str.strip()

# Convert time to datetime
df["time"] = pd.to_datetime(df["time"], errors="coerce")

# Helper to clean numeric values
def clean_value(val):
    if isinstance(val, str):
        val = (val.replace("mbar", "")
                  .replace("V", "")
                  .replace("uA", "")
                  .strip())
        return float(val) if val else None
    return val

# Clean pressure column
for col in df.columns:
    if "Pressure moving average" in col:
        df[col] = df[col].apply(clean_value)

#Get the number of pressure points for plots with numbers from 0 to N on ax axis
#pressSize = df.shape([0]) 
pressSize = len(df)
print("Size:",pressSize)
print("Enumerate:",enumerate(df["Pressure moving average"]))
print("Shape:",df.shape)

for i in range(0,pressSize):
     points.append(i)

# === DEFINE TIME WINDOW ===
# Use None for start/end if you don’t want filtering
time_ranges = {
    #1: ("2025-10-17 12:00:30", "2025-10-17 16:00:00"),  # Time range
    1: (None, None),  # Time range
}

# Plot data with time filter
for i in range(1, 2):
    press_col = f"Pressure moving average"

    if press_col not in df.columns:
        print(f"Skipping, missing data.")
        continue

    # Get range for this channel
    start_time, end_time = time_ranges.get(i, (None, None))

    mask = pd.Series(True, index=df.index)
    if start_time:
        mask &= df["time"] >= pd.to_datetime(start_time)
    if end_time:
        mask &= df["time"] <= pd.to_datetime(end_time)

    df_filtered = df.loc[mask]

    # Extract data
    #times = df_filtered["time"].to_numpy()
    points = np.array(points) 
    press_vals = pd.to_numeric(df_filtered[press_col], errors="coerce").to_numpy()

    print(df.shape)

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.set_title(f"Absolute pressure in the vessel in Time\n({start_time} → {end_time})")
    ax1.set_xlabel("Time")

    # Pressure axis
    ax1.set_ylabel("Absolute pressure [mbar]", color="tab:blue")
    ax1.plot(points, press_vals, color="tab:blue", label="time")
    ax1.tick_params(axis="y", labelcolor="tab:blue")

    fig.tight_layout()
    plt.grid(True, c='0.95')
    plt.show()
