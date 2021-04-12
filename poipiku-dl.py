import requests, argparse, sys, os, re, time, selenium
from termcolor import colored
from urllib.parse import urlparse
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise Directory(string)

def create_arg_parser():
    parser = argparse.ArgumentParser('python3 poipiku-dl.py',
                                     description='A tool to download pictures from Poipiku')
    parser.add_argument('-d', dest='PATH',
                        help='Path to directory where pictures will be saved', type=dir_path)
    parser.add_argument('-g', dest='geckodriver', default=None,
                        help='Set path to geckodriver executable. If not set, it\'s assumed that executable is in the same directory as script or in PATH')
    parser.add_argument('-c', dest='cookie', default=None,
                        help='Use cookie to get high resolution pictures. Limited resolution when not used')
    parser.add_argument('-q', default=False,
                        help='Run without output', action='store_true')
    parser.add_argument('URL', help='Address to account to be downloaded. Also works with only a set of pictures')
    return parser

def setup_webdriver():
    options = Options()
    options.headless = True
    if parsed_args.geckodriver is None:
        driver = webdriver.Firefox(service_log_path=os.path.devnull, options=options)
    else:
        driver = webdriver.Firefox(service_log_path=os.path.devnull, options=options, executable_path=parsed_args.geckodriver)
    return driver

def import_cookies(p):
    cookies = []
    # Copied this. Thanks StackOverflow
    with open(p, 'r') as f:
        for e in f:
            e = e.strip()
            if e.startswith('#'):
                continue
            k = e.split('\t')
            # Check for error in cookie. Length less than three means there's something wrong
            if len(k) < 3:
                continue
            cookies.append({'name': k[-2], 'value': k[-1], 'expiry': int(k[-3])})
    return cookies

def get_links():
    links = []
    # Will get links depending on what class we're looking for
    if webpage_mode in (3, 4):
        l = []
        if webpage_mode == 3:
            l = driver.find_elements_by_css_selector('[class="IllustItemImage"]')
        elif webpage_mode == 4:
            l = driver.find_elements_by_css_selector('[class="IllustItemThumbImg"]')

        for i in l:
            links.append(i.get_attribute('src'))
    else:
        l = []
        if webpage_mode == 1:
            l = driver.find_elements_by_css_selector('[class="IllustThumbImg"]')
        elif webpage_mode == 2:
            l = driver.find_elements_by_css_selector('[class="IllustItemThumb"]')

        for i in l:
            links.append(i.get_attribute('href'))
    return links

def write_files(url):
    # Apply name from URL
    filename = str(url).rsplit('/', 1)[1]
    filename = re.sub(r".jpeg_640.jpg", ".jpg", filename)
    filename = re.sub(r".png_640.jpg", ".jpg", filename)

    if os.path.isfile(filename):
        if parsed_args.q is False:
            if os.name == 'nt':
                print(colored(cwd + "\\" + filename, 'green'))
            else:
                print(colored(cwd + "/" + filename, 'green'))
    else:
        # For some reason this thing tries to write twice if cookie is not supplied, and I don't care enough to fix it. It works
        image = requests.get(str(url))
        with open(filename, 'wb') as f:
            f.write(image.content)
        if parsed_args.q is False:
            if os.name == 'nt':
                print(cwd + "\\" + filename)
            else:
                print(cwd + "/" + filename)

# webpage_mode decides what class to look for when scraping
# 1 = Base profile page
# 2 = Image list page
# 3 = Full-res image page if valid cookie is supplied
# 4 = Image page without cookie supplied
webpage_mode = int(1)

# Set some variables and load a bunch of startup-stuff
setcookie = False
arg_parser = create_arg_parser()
parsed_args = arg_parser.parse_args()
driver = setup_webdriver()
driver.get(parsed_args.URL)
page_links = get_links()
webpage_mode = int(2)

os.chdir(parsed_args.PATH)
cwd = os.getcwd()

for page_link in page_links:
    driver.get(page_link)

    # Load cookie if supplied
    if setcookie is False:
        if parsed_args.cookie is not None:
            cookies = import_cookies(parsed_args.cookie)
            for cookie in cookies:
                driver.add_cookie(cookie)
            time.sleep(2)
        setcookie = True
    
    # Load all images on image list page
    try:
        driver.find_element_by_css_selector('[class="BtnBase IllustItemExpandBtn"]').click()
        time.sleep(1)
    except selenium.common.exceptions.NoSuchElementException:
        pass
    
    # Load all image-links and fix array
    image_links = get_links()
    not_none_values = filter(None.__ne__, image_links)
    image_links = list(not_none_values)

    # Decide what classes to look for when getting image-links
    if parsed_args.cookie is not None:
        webpage_mode = int(3)
    else:
        webpage_mode = int(4)
        # Need to get image-links now before leaving page
        images = get_links()

    for image_link in image_links:
        # Load high-res image if cookie was supplied
        if webpage_mode == 3:
            driver.get(str(image_link))
            images = get_links()
        for image in images:
            # Ignore warning-images
            if "/warning" in str(image):
                continue
            else:
                write_files(str(image))
    webpage_mode = int(2)
driver.quit()
