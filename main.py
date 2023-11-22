###
### Goal: Open a folder, for each cbz, show the current cover image. Allow the user to enter a MangaDex url and then replace covers.
###


import os
import tkinter as tk

from window import ImageViewer

if __name__ == "__main__":
    current_directory = os.getcwd()

    root = tk.Tk()
    root.title("Image Viewer")
    viewer = ImageViewer(root)
    root.mainloop()
