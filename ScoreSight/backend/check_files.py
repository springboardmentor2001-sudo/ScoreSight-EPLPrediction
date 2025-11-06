# check_files.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ML_DIR = os.path.join(BASE_DIR, 'ml', 'models')

print("Current working directory:", os.getcwd())
print("Base directory:", BASE_DIR)
print("ML directory:", ML_DIR)

print("\nSearching for model files...")

# Search for all .pkl files in the project
for root, dirs, files in os.walk(BASE_DIR):
    for file in files:
        if file.endswith('.pkl'):
            print(f"Found: {os.path.join(root, file)}")

print("\nContents of ml/models directory:")
if os.path.exists(ML_DIR):
    for file in os.listdir(ML_DIR):
        print(f"  - {file}")
else:
    print("  ml/models directory does not exist!")