import base64
import os
import zipfile
import requests
from tkinter import filedialog

from PIL import Image, ImageTk
import tkinter as tk
from io import BytesIO

import webdriver_util
from parser import parse_volume


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
                                                if file.lower().endswith(
                            ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'))]

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
        vol_num = parse_volume(cbz_file)
        if vol_num is None:
            continue
        zip_path = os.path.join(directory, cbz_file)
        first_image, image_data = find_first_image(zip_path)

        if first_image:
            result_data.append({
                'filename': cbz_file,
                'first_image_path': first_image,
                'base64_image': image_data,
                'volume_num': vol_num
            })

    return result_data


def find_covers(search_term):
    if '?' in search_term:
        search_term = search_term.split('?')[0] + '?tab=art'
    search_term = 'https://mangadex.org/title/af96c6a2-b3f7-405b-821a-019fed3d44db/uchi-no-musume-ni-te-o-dasu-na-amazing-eighth-wonder?tab=art'

    print(f"Downloading covers for: {search_term}")
    driver = webdriver_util.init_chrome(headless=False)
    webdriver_util.get_url(driver, search_term)
    webdriver_util.sleep(1)

    # Check if Content Warning
    potential_content_warning_elem = webdriver_util.verify_elem(driver, '.md-content > div > span')
    if potential_content_warning_elem is not None and potential_content_warning_elem.text == 'Content Warning':
        webdriver_util.verify_elem(driver, 'button.primary').click()
        webdriver_util.sleep(1)

    # Get all Images
    images = []

    image_elems = webdriver_util.verify_elems(driver, 'a.group > img[alt="Cover image"]')
    subtitle_elems = webdriver_util.verify_elems(driver, 'a.group > .subtitle')

    for index, img_elem in enumerate(image_elems):
        # First is the cover image of the page
        if index == 0:
            continue
        image_src = img_elem.get_attribute('src')
        image_content = requests.get(image_src).content
        image_base64 = base64.b64encode(image_content).decode('utf-8')

        volume_number = subtitle_elems[index - 1].text
        images.append({'src': image_base64, 'vol': volume_number})

    return images


class ImageViewer:
    def __init__(self, master):
        self.master = master
        self.result_data = []
        self.images = []

        self.folder_button = tk.Button(master, text="Open Folder", command=self.open_folder)
        self.folder_button.grid(row=0, column=0, padx=5, pady=5)

        self.url_entry = tk.Entry(master, width=50)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5)

        self.download_button = tk.Button(master, text="Download Covers", command=self.download_covers,
                                         state=tk.DISABLED)
        self.download_button.grid(row=0, column=2, padx=5, pady=5)

        self.stack_frames = []  # To keep track of the stack frames for later updates

        master.grid_rowconfigure(1, weight=1)

    def open_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.result_data = process_directory(folder_path)
            self.update_ui()

    def download_covers(self):
        search_term = self.url_entry.get()
        self.images = find_covers(search_term)
        self.merge_images()
        self.update_ui()

    def merge_images(self):
        for image in self.images:
            vol_number = image['vol']

            for item in self.result_data:
                if 'volume_num' in item and item['volume_num'] is None:
                    continue
                vol_label = f"Volume {item['volume_num']}"
                if vol_label == vol_number:
                    item['target_img'] = image['src']
                    item['downloaded_vol'] = vol_number
                    break

    def update_ui(self):
        # Remove existing stack frames
        for frame in self.stack_frames:
            frame.destroy()

        # Create a new stack for each item in result_data
        for i, item in enumerate(self.result_data):
            stack_frame = tk.Frame(self.master)
            stack_frame.grid(row=1, column=i, padx=5, pady=5)

            image_data = base64.b64decode(item['base64_image'])
            image = Image.open(BytesIO(image_data))
            image.thumbnail((150, 150))
            tk_image = ImageTk.PhotoImage(image)

            label_image = tk.Label(stack_frame, image=tk_image)
            label_image.image = tk_image
            label_image.grid(row=0, column=0, padx=5)

            label_filename = tk.Label(stack_frame, text=f"Filename: {item['filename']}")
            label_filename.grid(row=1, column=0, padx=5)

            checkbox_var = tk.IntVar()
            checkbox = tk.Checkbutton(stack_frame, variable=checkbox_var)
            checkbox.grid(row=2, column=0)

            if 'target_img' in item:
                target_img_data = base64.b64decode(item['target_img'])
                target_img = Image.open(BytesIO(target_img_data))
                target_img.thumbnail((150, 150))
                tk_target_img = ImageTk.PhotoImage(target_img)

                label_target_img = tk.Label(stack_frame, image=tk_target_img)
                label_target_img.image = tk_target_img
                label_target_img.grid(row=0, column=1, padx=5)

                label_downloaded_vol = tk.Label(stack_frame, text=f"Downloaded Volume: {item['downloaded_vol']}")
                label_downloaded_vol.grid(row=1, column=1, padx=5)
            else:
                label_missing = tk.Label(stack_frame, text="MISSING", foreground="red")
                label_missing.grid(row=0, column=1, padx=5)

            # Save the frame to the list for later updates
            self.stack_frames.append(stack_frame)

        # Enable the Download Covers button
        self.download_button.config(state=tk.NORMAL)
