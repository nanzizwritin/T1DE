from ImageInput import pick_image
from StraightenImage import straighten_image
from RecognitionOfData import extract_data
from CreateDB import create_db
from ui import fix_readings
from Analysis import analyse

def run():
    pick_image()
    straighten_image()
    grid = extract_data()
    create_db(grid)
    fix_readings()
    analyse()


if __name__ == "__main__":
    run()