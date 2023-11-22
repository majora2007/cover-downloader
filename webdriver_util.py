from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

import time
import os
import shutil

wait_time = 30

from os import chdir, environ
from os.path import join, dirname
import sys


def pyinstaller_get_full_path(filename):
    """ If bundling files in onefile with pyinstaller, use thise to get the temp directory where file actually resides """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller >= 1.6
		# chdir(sys._MEIPASS)
        filename = join(sys._MEIPASS, filename)
    elif '_MEIPASS2' in environ:
        # PyInstaller < 1.6 (tested on 1.5 only)
		# chdir(environ['_MEIPASS2'])
        filename = join(environ['_MEIPASS2'], filename)
    else:
        # chdir(dirname(sys.argv[0]))
        filename = join(dirname(sys.argv[0]), filename)

    return filename


def init_chrome(download_dir='', headless=True):
    opts = webdriver.ChromeOptions()
    opts.add_argument('--no-sandbox')
    if headless:
        opts.add_argument("--headless")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1200")
    opts.add_argument("--ignore-certificate-errors")
    opts.add_argument("--disable-blink-features")
    opts.add_argument('--disable-blink-features=AutomationControlled')
    opts.add_argument("--disable-extensions")
    opts.add_experimental_option('useAutomationExtension', False)
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])

    if download_dir != '':
        print('Download Directory: {0}'.format(download_dir))
        prefs = {'download.default_directory': download_dir}
        opts.add_experimental_option('prefs', prefs)
    print('Opening Chrome')

    driver = webdriver.Chrome(opts)
    return driver


def switch_to_frame(driver, id):
    print('Switching to {0} iFrame'.format(id))
    # wait_for_iframe(driver, '//iframe[id="ngtModule"]')
    driver.switch_to_frame(id)


# TODO: Ensure the iframe is loaded
# verify_iframe(driver, 'iframe[id="ngtModule"]')
# driver.frame_to_be_available_and_switch_to_it('ngtModule')

def switch_to_window(driver):
    print('Switching to new window')
    for handle in driver.window_handles:
        driver.switch_to_window(handle)


def verify_iframe(driver, selector):
    WebDriverWait(driver, wait_time).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, selector)))


def verify_elem(driver, selector):
    elem = WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    return elem


def verify_elem_xpath(driver, selector):
    elem = WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.XPATH, selector)))
    return elem


def verify_elems(driver, selector):
    WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    elems = driver.find_elements_by_css_selector(selector)
    return elems


def sleep(t):
    print('Sleeping for {0} seconds'.format(t))
    time.sleep(t)  # Wait for a few seconds


def get_url(driver, url):
    print('Fetching {0}'.format(url))
    driver.get(url)


def verify_file(path, filename):
    full_path = os.path.join(path, filename)
    print('Verifying file exists: {0}'.format(full_path))
    while not os.path.exists(full_path):
        time.sleep(1)