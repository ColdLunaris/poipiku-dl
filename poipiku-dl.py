import requests, argparse, sys, os, re, time, selenium
from termcolor import colored
from urllib.parse import urlparse
from bs4 import BeautifulSoup
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
                                     description='a tool to download pictures from Poipiku')
    parser.add_argument('-d', dest='PATH',
                        help='path to directory where pictures will be saved', type=dir_path)
    parser.add_argument('-g', dest='geckodriver', default=False,
                        help='set path to geckodriver executable. If not set, it\'s assumed that executable is in the same directory as script')
    parser.add_argument('-q', default=False,
                        help='run without output', action='store_true')
    parser.add_argument('URL', help='address to account to be downloaded. Also works with only a set of pictures')
    return parser

def setup_webdriver():
    options = Options()
    options.headless = True
    if parsed_args.geckodriver is False:
        driver = webdriver.Firefox(service_log_path=os.path.devnull, options=options)
    else:
        driver = webdriver.Firefox(service_log_path=os.path.devnull, options=options, executable_path=parsed_args.geckodriver)
    return driver

def get_page_links():
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    r = requests.get(parsed_args.URL, headers = headers)
    soup = BeautifulSoup(r.text, 'html.parser')

    links = [a['href'] for a in soup.find_all('a', href = re.compile('^/IllustViewPcV.jsp\?'))]
    return links

def get_image_links():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    images = soup.find_all('img', {'src':re.compile('.jpg')})
    return images

def set_filename(url):
    a = urlparse(url)
    filename = os.path.basename(a.path)
    filename = re.sub(r".jpeg_640.jpg", ".jpg", filename)
    filename = re.sub(r".png_640.jpg", ".jpg", filename)
    return filename

image_urls = []
arg_parser = create_arg_parser()
parsed_args = arg_parser.parse_args(sys.argv[1:])
driver = setup_webdriver()
page_links = get_page_links()
os.chdir(parsed_args.PATH)
cwd = os.getcwd()

for page_link in page_links:
    page_link = 'https://poipiku.com' + page_link
    driver.get(page_link)
    try:
        driver.find_element_by_css_selector('[class="BtnBase IllustItemExpandBtn"]').click()
        time.sleep(1)
    except selenium.common.exceptions.NoSuchElementException:
        pass

    images = get_image_links()


    for image in images:
        path = image['src']
        url = re.sub(r"//", "https://", path)
        if "/warning" in path:
            continue
        if url not in image_urls:
            image_urls.append(url)
            response = requests.get(url)
            filename = set_filename(url)
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
driver.quit()
