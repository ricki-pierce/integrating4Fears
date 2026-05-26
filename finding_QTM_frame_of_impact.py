import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# Replace this with your Excel file path
#file_path = r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\trc files\drop_Trial1_eyecamera.xlsx"
#file_path = r"C:\Users\rpier12\Desktop\Marker Tests 51326 Roun 2\trc files\drop_Trial10_rickiround2.xlsx"
file_path = r"C:\Users\rpier12\Desktop\Marker Test 520\trc files\drop_Trial20_ricki520.xlsx"

# Read data
df = pd.read_excel(file_path, header=None, skiprows=6, usecols="A:E")
df.columns = ["Frame","Time","X","Y","Z"]

df.fillna(0, inplace=True)
df["Time"] = pd.to_numeric(df["Time"])
df["Y"] = pd.to_numeric(df["Y"])

# Remove frames where marker wasn't visible
df = df[df["Y"] != 0].reset_index(drop=True)

time = df["Time"].values
y = df["Y"].values

# Find highest point
max_idx = np.argmax(y)

# First and second derivatives
v = np.gradient(y, time)
a = np.gradient(v, time)

# Only look AFTER the peak
search_region = a[max_idx+1:]

# Find sharpest V (largest curvature)
impact_idx = np.argmax(search_region) + max_idx + 1

frame = df.loc[impact_idx, "Frame"]
time_impact = df.loc[impact_idx, "Time"]
y_impact = df.loc[impact_idx, "Y"]

print("Impact detected:")
print(f"Frame: {frame}")
print(f"Time: {time_impact:.6f} s")
print(f"Y Position: {y_impact:.3f} mm")



# --- Plot 1: X, Y, Z vs Time ---
plt.figure(figsize=(10, 6))
plt.plot(df["Time"], df["X"], label="X")
plt.plot(df["Time"], df["Y"], label="Y")
plt.plot(df["Time"], df["Z"], label="Z")
plt.xlabel("Time (s)")
plt.ylabel("Position (mm)")
plt.title("X, Y, Z vs Time")
plt.legend()
plt.grid(True)
plt.show()

# --- Plot 2: Y vs Time ---
plt.figure(figsize=(10, 6))
plt.plot(df["Time"], df["Y"], label="Y", color="orange")
plt.axhline(y=300, color="red", linestyle="--", label="Y = 300 mm")

plt.xlabel("Time (s)")
plt.ylabel("Y Position (mm)")
plt.title("Y vs Time")
plt.grid(True)
plt.show()
