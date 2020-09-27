import sys, re, os, time, wget, requests
from termcolor import colored
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

# Get URL and current working directory for file-naming
site = sys.argv[1]
cwd = os.getcwd()

# Set firefox to be quiet and load webpage
options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)
driver.get(site)

# Check for "Show more" buttons. If present, load all images, else ignore
button = driver.execute_script("return document.getElementsByClassName('BtnBase IllustItemExpandBtn')[0]")
if button:
    driver.execute_script("document.getElementsByClassName('BtnBase IllustItemExpandBtn')[0].click()")
    time.sleep(1)
else:
    pass

# Parse page-source and extract only picture-links
src = driver.page_source
soup = BeautifulSoup(src, 'html.parser')
img_tags = soup.find_all('img', {'src':re.compile('.jpg')})

for img in img_tags:
    # Fix URLs and load image
    path = img['src']
    url = re.sub(r"//", "https://", path)
    response = requests.get(url)

    # Create a filename. Replace redudant info in filename
    a = urlparse(url)
    filename = os.path.basename(a.path)
    filename = re.sub(r".jpeg_640.jpg", ".jpg", filename)

    # If file already exists, print green text and don't save anything
    if os.path.isfile(filename):
        # Find OS-version, and apply folder structure to show complete filepath
        if os.name == 'nt':
            print(colored(cwd + "\\" + filename, 'green'))
        else:
            print(colored(cwd + "/" + filename, 'green'))
        continue
    else:
        # Write image to file. Print full path in default terminal colors afterwards
        with open(filename, 'wb') as f:
            f.write(response.content)
        if os.name == 'nt':
            print(cwd + "\\" + filename)
        else:
            print(cwd + "/" + filename)

driver.close()