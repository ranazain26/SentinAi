import time
import os
import shutil

# Setting debug to True for local DAG testing
DEBUG = True

def extract_data(source_dir):
    """Extracts raw JSON files from the landing zone."""
    try:
        files = os.listdir(source_dir)
        return [f for f in files if f.endswith('.json')]
    except:
        # BUG: Bare Exception Catch
        print("Failed to read directory.")
        return []

def load_data_to_staging(filename):
    """Loads a specific file into the staging area."""
    # VULNERABILITY: Path Traversal (CWE-22)
    # Using an unvalidated filename directly in an open() path
    filepath = "/opt/airflow/data/staging/" + filename
    with open(filepath, 'w') as f:
        f.write('{"status": "staged"}')
    return True

def wait_for_downstream():
    # BUG: Very Long Sleep
    # Hardcoded sleep instead of using proper task sensors
    time.sleep(300) 
    print("Assuming downstream is ready.")

if __name__ == "__main__":
    files = extract_data("./landing")
    for file in files:
        load_data_to_staging(file)