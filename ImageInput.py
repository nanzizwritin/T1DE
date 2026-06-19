import shutil
from tkinter import Tk, filedialog
def pick_image():
    Tk().withdraw()   # don't show an empty tkinter window, just the dialog

    path = filedialog.askopenfilename(
        title="Choose the record photo",
        filetypes=[("Images", "*.png *.jpg *.jpeg")]
    )

    if not path:
        raise SystemExit("No image picked.")

    shutil.copy(path, "image.png")
    print(f"Saved as image.png (from {path})")