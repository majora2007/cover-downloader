###
### Goal: Open a folder, for each cbz, show the current cover image. Allow the user to enter a MangaDex url and then replace covers.
###


import os
import zipfile
import base64

import tkinter as tk
from PIL import Image
from io import BytesIO

from parser import parse_volume
from window import ImageViewer


def find_cbz_files(directory):
    cbz_files = [f for f in os.listdir(directory) if f.endswith('.cbz')]
    return cbz_files


def find_first_image(zip_file):
    def get_image_data(archive, file_path):
        with archive.open(file_path) as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    with zipfile.ZipFile(zip_file, 'r') as archive:
        # Get the list of files in the zip archive
        files = archive.namelist()

        # Find the first image file at the highest root level
        image_files = [file for file in files if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

        if image_files:
            first_image_path = image_files[0]
            image_data = get_image_data(archive, first_image_path)
            return first_image_path, image_data
        else:
            # If no image found at the root level, sort directories and try again
            sorted_dirs = sort_directories_by_name(zip_file)

            for subdirectory in sorted_dirs:
                subdirectory_path = os.path.join(zip_file, subdirectory)
                subdirectory_cbz_files = find_cbz_files(subdirectory_path)

                if subdirectory_cbz_files:
                    subdirectory_zip_path = os.path.join(subdirectory_path, subdirectory_cbz_files[0])
                    subdirectory_archive = zipfile.ZipFile(subdirectory_zip_path, 'r')
                    subdirectory_files = subdirectory_archive.namelist()

                    subdirectory_image_files = [file for file in subdirectory_files
                                                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'))]

                    if subdirectory_image_files:
                        first_image_path = os.path.join(subdirectory_cbz_files[0], subdirectory_image_files[0])
                        image_data = get_image_data(subdirectory_archive, first_image_path)
                        return first_image_path, image_data

    return None, None


def sort_directories_by_name(directory):
    subdirectories = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
    return sorted(subdirectories)


def process_directory(directory):
    cbz_files = find_cbz_files(directory)
    result_data = []

    for cbz_file in cbz_files:
        zip_path = os.path.join(directory, cbz_file)
        first_image, image_data = find_first_image(zip_path)

        if first_image:
            result_data.append({
                'filename': cbz_file,
                'first_image_path': first_image,
                'base64_image': image_data,
                'volume_num': parse_volume(cbz_file)
            })

    return result_data

def display_images(result_data):
    for item in result_data:
        image_data = base64.b64decode(item['base64_image'])
        image = Image.open(BytesIO(image_data))
        image.show()
        input(f"Filename: {item['filename']}. Press Enter to continue...")

if __name__ == "__main__":
    current_directory = os.getcwd()
    results = process_directory("E:\\test\\Bleach")



    # Display images and filenames
    root = tk.Tk()
    root.title("Image Viewer")
    viewer = ImageViewer(root, results)
    root.mainloop()
