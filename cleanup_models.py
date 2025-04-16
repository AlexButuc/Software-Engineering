import os
import glob

# Find all individual model .pkl files
model_files = glob.glob("occupancy_model_station_*.pkl")

# Delete each one
for file in model_files:
    try:
        os.remove(file)
        print(f"Deleted: {file}")
    except Exception as e:
        print(f"Failed to delete {file}: {e}")

print(" Cleanup complete.")
