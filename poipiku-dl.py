# -------------------------------------------------------------------
# This script can be used to download an entire Poipiku-profile.
#
# The user must supply a cookie (or dont i have no idea how the
# script reacts to that) that is logged in to poipiku with a valid
# account (currently only tested with a Twitter-account). The cookie
# has to be a Netscape HTTP Cookie File (exported from Firefox). I 
# haven't tested with any other types of cookies, ie. from Chrome.
# The script is slow as all hell, so if anyone wants to improve its
# speed, feel free to do so.
# -------------------------------------------------------------------

import requests, json, re, os, argparse, asyncio, concurrent.futures
from termcolor import colored
from bs4 import BeautifulSoup

# Static urls used for POSTing payloads to retrieve urls
url_append_file = "https://poipiku.com/f/ShowAppendFileF.jsp"
url_illust_detail = "https://poipiku.com/f/ShowIllustDetailF.jsp"

# We don't want to download a bunch of warnings and whatnot. Skipping these
skips = [
        '"IllustItemThumbImg" src="/img/publish_pass"',
        '"IllustItemThumbImg" src="/img/warning"',
        '"IllustItemThumbImg" src="/img/publish_login"'
    ]

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("-d", dest="directory", required=False, help="destination where all images will be saved")
    p.add_argument("-c", dest="cookie", required=True, help="path to authenticated cookie-file")
    p.add_argument("-u", dest="url", required=True, help="url for profile to be downloaded")
    p.add_argument("-v", dest="verbose", required=False, default=True, help="specifies verbosity to true or false. Default true")
    p.add_argument("-t", dest="threads", required=False, help="amount of threads to spawn while downloading. Default is 1")
    p.add_argument("-p", dest="password", required=False, help="password for protected pages. Default is yes or none depending on if the site asks for a password")
    args = p.parse_args()

    return args

def import_cookie(cookie):
    from http.cookiejar import MozillaCookieJar
    cj = MozillaCookieJar(cookie)
    cj.load(ignore_expires=True, ignore_discard=True)

    return cj

# This is a fucking magic payload... Check get_image_site() for info on why
def create_post_append_data(uid, iid, pas):
    payload = {
        'UID': uid,
        'IID': iid,
        'PAS': pas,
        'MD': '0',
        'TWF': '-1',
    }
    return payload

def create_post_detail_data(id, td, ad):
    payload = {
        'ID': id,
        'TD': td,
        'AD': ad,
    }
    return payload

def create_post_detail_data_with_pass(id, td, ad, pas):
    payload = {
        'ID': id,
        'TD': td,
        'AD': ad,
        'PAS': pas
    }
    return payload

# Poipiku expects very specific headers. This one seems to work fine
def create_session(referer, cookie):
    s = requests.Session()
    s.headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Referer': referer,
        'Origin': 'https://poipiku.com'
    }
    s.cookies = import_cookie(cookie)

    return s

def get_image_urls(response):
    raw_json = json.loads(response.text)
    raw_html = raw_json['html']

    # Getting direct links to high quality images from image page
    urls = ['https:' + url for url in re.findall('"(.*?)"', raw_html) if 'img-org.poipiku.com' in url]

    return urls

def save_image(session, url, path, v):
    name = url.rsplit('/', 1)[-1]
    path = path + '/' + name

    if os.path.exists(path):
        if v is True:
            print(colored(path, 'green'))
        return

    r = session.get(url, stream=True)

    if r.status_code == 200:
        # Write file in chunks. Slow, but works, so it's whatever...
        with open(path, 'wb') as f:
            for c in r:
                f.write(c)
        if v is True:
            print(colored(path, 'white'))

# Cycle through all pages on profile page to get all urls
def get_image_pages(session, url):
    reverse_sites = []
    r = session.get(url)

    soup = BeautifulSoup(r.text, 'html.parser')
    pages = soup.findAll(class_="BtnBase PageBarItem")

    # Get ready for a clusterfuck... It works though, cycles through every single page on a given profile and retrieves all urls
    if len(pages) > 2:
        current_page = 'https://poipiku.com' + str(pages[0]).split('href="')[1].split('"><')[0].replace('amp;', '')
        next_page = 'https://poipiku.com' + str(pages[-1]).split('href="')[1].split('"><')[0].replace('amp;', '')

        # Get all image pages on all pages on profile (page 1, page 2 etc.)
        # Unfortunately ignores last page since current_page then equals
        # next_page, so another lookup is done after loop to get everything
        while current_page != next_page:
            response_current = session.get(current_page)
            soup_current = BeautifulSoup(response_current.text, 'html.parser')

            for site in soup_current.findAll("a", class_="IllustInfo"):
                url = 'https://poipiku.com' + str(site).split('href="')[1].split('"><')[0]
                reverse_sites.append(url)
            
            response_next = session.get(next_page)
            soup_next = BeautifulSoup(response_next.text, 'html.parser')
            current_page = 'https://poipiku.com' + str(soup_next.findAll(class_="BtnBase PageBarItem Selected")[0]).split('href="')[1].split('">')[0].replace('amp;', '')
            next_page = 'https://poipiku.com' + str(soup_next.findAll(class_="BtnBase PageBarItem")[-1]).split('href="')[1].split('"><')[0].replace('amp;', '')
        
        # Need to run one last time to get last page
        response = session.get(current_page)
        soup = BeautifulSoup(response.text, 'html.parser')
        for site in soup.findAll("a", class_="IllustInfo"):
                url = 'https://poipiku.com' + str(site).split('href="')[1].split('"><')[0]
                reverse_sites.append(url)

    else:
        for site in soup.findAll("a", class_="IllustInfo"):
            url = 'https://poipiku.com' + str(site).split('href="')[1].split('"><')[0]
            reverse_sites.append(url)

    # I want this script to work like gallery-dl, and it downloads
    # the oldest images first, so reversing the order of urls to
    # check so oldest images are downloaded first
    sites = reverse_sites[::-1]

    return sites

# Create directory based on given argument and username
def create_directory(session, url, directory):
    r = session.get(url)

    path = os.getcwd() if directory is None else directory
    if not path.endswith('/'):
        path = path + "/"

    soup = BeautifulSoup(r.text, 'html.parser')

    # First method is preferred, fallback to URL if no background image is provided
    id = ''
    try:
        id = str(soup.find('style')).split("url('//")[1].split('/')[2].lstrip('0')
    except Exception:
        id = url.split('.com/')[1]

    # It's not me who messed up the classname, it's poipiku...
    try:
        username = soup.find(class_="UserInfoProgile")
        path = path + id + ' ' + str(username).split("@")[1].split("<")[0]
    except Exception:
        username = soup.find(class_="UserInfoUserName")
        path = path + id + ' ' + str(username).split('">')[2].split("</")[0]
        
    if not os.path.exists(path):
        os.makedirs(path)

    # Need full directory for later in main
    return path

def get_image_site(session, url, path, verbose, pas):
    inital_response = session.get(url)

    uid = url.split('/')[3]
    iid = url.split('/')[4].split('.')[0]

    if "IllustItemExpandPass" in inital_response.text:
        pas = 'yes' if pas is None else pas
        payload = create_post_detail_data_with_pass(uid, iid, '-1', pas)
    else:
        payload = create_post_detail_data(uid, iid, '-1')

    if not any(x in inital_response.text for x in skips):
        response = session.post(url_illust_detail, data=payload)
        urls = get_image_urls(response)
        for url in urls:
            save_image(session, url, path, verbose)
    
    session.close()

async def main():
    args = parse_args()

    with create_session(args.url, args.cookie) as s:
        r = s.get(args.url)
        path = create_directory(s, args.url, args.directory)
        
        # Save background image
        soup = BeautifulSoup(r.text, 'html.parser')
        try:
            background_image = 'https://' + str(soup.find('style')).split("url('//")[1].split("');")[0].split("_640")[0]
            save_image(s, background_image, path, args.verbose)
        except Exception:
            pass
        
        sites = get_image_pages(s, args.url)
        threads = 1 if args.threads is None else int(args.threads)

        with concurrent.futures.ThreadPoolExecutor(threads) as executor:
            loop = asyncio.get_event_loop()

            tasks = [
                loop.run_in_executor(
                    executor,
                    get_image_site,
                    *(create_session(site, args.cookie), site, path, args.verbose, args.password)
                )
                for site in sites
            ]
            for response in await asyncio.gather(*tasks):
                pass

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
    loop.close()
