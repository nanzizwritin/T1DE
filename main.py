from ImageInput import pick_image
from StraightenImage import straighten_image
from RecognitionOfData import extract_data
from CreateDB import create_db
from Analysis import analyse
import subprocess

def fix_readings():
    subprocess.run(["streamlit", "run", "ui.py"])   # opens the review screen

def run():
    pick_image()
    straighten_image()
    grid = extract_data()
    create_db(grid)
    fix_readings()
    analyse()


if __name__ == "__main__":
    run()