import base64
import os

from PIL import Image, ImageTk
import tkinter as tk
from io import BytesIO

import webdriver_util


def merge_images(result_data, images):
    result_data_dict = {item['filename']: item for item in result_data}

    for image in images:
        vol_number = image['vol']
        filename = f"Volume {vol_number}"  # Adjust this to match your filename format

        if filename in result_data_dict:
            result_data_dict[filename]['target_img'] = image['src']

    return result_data_dict


class ImageViewer:
    def __init__(self, master, result_data):
        self.images = []
        self.master = master
        self.result_data = result_data
        self.current_page = 0
        self.items_per_page = 4

        self.label_images = []
        self.label_filenames = []

        self.canvas = tk.Canvas(master, borderwidth=0, background="#ffffff", height=150)
        self.h_scrollbar = tk.Scrollbar(master, orient="horizontal", command=self.canvas.xview)

        self.canvas.config(xscrollcommand=self.h_scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        self.frame = tk.Frame(self.canvas)
        self.canvas.create_window((4, 4), window=self.frame, anchor="nw")

        self.entry = tk.Entry(master, width=80)
        self.entry.grid(row=2, column=0, padx=5, pady=5, columnspan=3)

        self.download_button = tk.Button(master, text="Download", command=self.download_covers)
        self.download_button.grid(row=3, column=0, columnspan=1, pady=5)

        self.show_images()

        # Configure grid weights to make the canvas and scrollbar expand
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)

    def download_covers(self):
        # Add your download logic here
        search_term = self.entry.get()
        search_term = 'https://mangadex.org/title/af96c6a2-b3f7-405b-821a-019fed3d44db/uchi-no-musume-ni-te-o-dasu-na-amazing-eighth-wonder?tab=art'
        # Use the search_term to download covers or perform any other action
        print(f"Downloading covers for: {search_term}")
        driver = webdriver_util.init_chrome(headless=False, download_dir=os.getcwd())
        webdriver_util.get_url(driver, search_term)
        webdriver_util.sleep(1)

        # Check if Content Warning
        potential_content_warning_elem = webdriver_util.verify_elem(driver, '.md-content > div > span')
        if potential_content_warning_elem is not None and potential_content_warning_elem.text == 'Content Warning':
            webdriver_util.verify_elem(driver, 'button.primary').click()
            webdriver_util.sleep(1)

        # Get all Images
        self.images = []
        anchor_elements = webdriver_util.verify_elems(driver, 'a.group')
        for anchor in anchor_elements:
            # Extract the src attribute from the image
            image_src = anchor.find_element_by_css_selector('img').get_attribute('src')

            # Extract the volume number
            volume_number = anchor.find_element_by_css_selector('.subtitle').text

            # Append the result as a dictionary to the array
            self.images.append({'src': image_src, 'vol': volume_number})

        merge_images(self.result_data, self.images)

    def show_images(self):
        for label_image in self.label_images:
            label_image.grid_forget()
        self.label_images = []

        for label_filename in self.label_filenames:
            label_filename.grid_forget()
        self.label_filenames = []

        for i, item in enumerate(self.result_data):
            image_data = base64.b64decode(item['base64_image'])
            image = Image.open(BytesIO(image_data))
            image.thumbnail((150, 150))
            tk_image = ImageTk.PhotoImage(image)

            label_image = tk.Label(self.frame, image=tk_image)
            label_image.image = tk_image
            label_image.grid(row=0, column=i, padx=5)

            label_filename = tk.Label(self.frame, text=f"Filename: {item['filename']}")
            label_filename.grid(row=1, column=i, padx=5)

            self.label_images.append(label_image)
            self.label_filenames.append(label_filename)

        self.frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))