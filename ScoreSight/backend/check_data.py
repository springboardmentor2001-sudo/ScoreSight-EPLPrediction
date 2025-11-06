import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

print("DATA_DIR:", DATA_DIR)
print("\nChecking if data directory exists:", os.path.exists(DATA_DIR))
print("\nFiles in data directory:")

if os.path.exists(DATA_DIR):
    for file in os.listdir(DATA_DIR):
        full_path = os.path.join(DATA_DIR, file)
        print(f"  - {file}")
        print(f"    Full path: {full_path}")
        print(f"    Exists: {os.path.exists(full_path)}")
else:
    print("Data directory does not exist!")

print("\nLooking for CSV file specifically:")
csv_path = os.path.join(DATA_DIR, 'master_data_with_features.csv')
print(f"Expected path: {csv_path}")
print(f"File exists: {os.path.exists(csv_path)}")