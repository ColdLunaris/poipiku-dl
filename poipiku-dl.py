import sys, re, os, time, requests, argparse

from termcolor import colored
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


# Check if defined dir-path exists. If not, throw exception
def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise Directory(string)

# Create argument-parser. Supported arguments are output-dir, quiet and URL
def create_arg_parser():
    parser = argparse.ArgumentParser('python3 poipiku-dl.py', 
                                     description='a tool to download pictures from Poipiku')
    parser.add_argument('-d', dest='PATH',
                        help='path to directory where pictures will be saved', type=dir_path)
    parser.add_argument('-g', dest='geckodriver', default=False,
                        help='set path to geckodriver executable. If not set, it\'s assumed that executable is in the same directory as script')
    parser.add_argument('-q', default=False,
                        help='run without output', action='store_true')
    parser.add_argument('URL', help='address to account to be downloaded. Also works with only a set of pictures')
    return parser

# Turn off logging, set driver in headless-mode and specify geckodriver-location if needed
def setup_webdriver():
    options = Options()
    options.headless = True
    if parsed_args.geckodriver is False:
        driver = webdriver.Firefox(service_log_path=os.path.devnull, options=options)
    else:
        driver = webdriver.Firefox(service_log_path=os.path.devnull, options=options, executable_path=parsed_args.geckodriver)
    return driver

# Check for "Show more" buttons. If present, show all images, else ignore
def javascript_button_clicker():
    count = 0
    buttons = driver.execute_script("return document.getElementsByClassName('BtnBase IllustItemExpandBtn')")
    for button in buttons:
        driver.execute_script("document.getElementsByClassName('BtnBase IllustItemExpandBtn')[" + str(count) + "].click()")
        count += 1
        time.sleep(1)
    else:
        pass

# Parse page-source and extract only image-links
def get_image_links():
    src = driver.page_source
    soup = BeautifulSoup(src, 'html.parser')
    images = soup.find_all('img', {'src':re.compile('.jpg')})
    return images

# Create filenames. Replace redudant info in filename
def set_filename(url):
    a = urlparse(url)
    filename = os.path.basename(a.path)
    filename = re.sub(r".jpeg_640.jpg", ".jpg", filename)
    filename = re.sub(r".png_640.jpg", ".jpg", filename)
    return filename

arg_parser = create_arg_parser()
parsed_args = arg_parser.parse_args(sys.argv[1:])

cwd = os.getcwd()

# Set firefox to be quiet, load webpage and get all pictures
driver = setup_webdriver()
driver.get(parsed_args.URL)
javascript_button_clicker()
images = get_image_links()

for image in images:
    # Fix URLs and load image
    path = image['src']
    url = re.sub(r"//", "https://", path)

    # Ignore warning-pictures
    if "/warning" in path:
        continue

    response = requests.get(url)
    filename = set_filename(url)

    os.chdir(parsed_args.PATH)
    cwd = os.getcwd()
    
    # Save images to working dir/specified dir unless they already exist
    if os.path.isfile(filename):
        if parsed_args.q is False:
            if os.name == 'nt':
                print(colored(cwd + "\\" + filename, 'green'))
            else:
                print(colored(cwd + "/" + filename, 'green'))
        else:
            continue
    else:
        with open(filename, 'wb') as f:
                f.write(response.content)
        if parsed_args.q is False:
            if os.name == 'nt':
                print(cwd + "\\" + filename)
            else:
                print(cwd + "/" + filename)
        else:
            continue
driver.close()