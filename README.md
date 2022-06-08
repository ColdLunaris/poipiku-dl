# poipiku-dl

A tool written in Python to download images from poipiku. Tested on Linux. 

## Requirements
Some pip modules are needed for poipiku-dl to work. Some of them are already pre-installed on your system. Copy-paste this command and you should be good here:

`pip3 install requests termcolor beautifulsoup4`

If you still get an error for missing modules, that's when Google helps you out.


## How to use
| Argument | Description |
| --- | --- |
| `-v VALUE` | Output URLs while downloading. Either True or False. True if not specified |
| `-d PATH` | Specify output-directory. Current directory if not specified |
| `-c PATH-TO-COOKIES-FILE` **REQUIRED** | Specify path to cookies with Poipiku-login |
| `-u URL` **REQUIRED**| Specifies which link to look for images | 
| `-t THREADS` | Specifies how many threads to use for downloads. Default is 1 | 
| `-p PASSWORD` | Specifies password for protected pages. Default is 'yes' or empty if page doesn't require password | 


`python3 ./poipiku-dl.py [-v VALUE] [-d PATH] [-c PATH-TO-COOKIES-FILE] -u 'enter URL here in quotes'`

### Use with cookie
Poipiku locks links for full-res images behind a login. You can supply already authenticated cookies by passing `-c` and specifying the txt-file. Open https://poipiku.com/ in Firefox and log in. Once logged in, use Export Cookies for Firefox, as it's the only one I've tested and know works, and export cookies for poipiku.com. You're on your own if you choose not to. Get the extension here: https://addons.mozilla.org/en-US/firefox/addon/export-cookies-txt/. I've only tested with a Twitter-login, so I don't know if any other forms of logins work.

### Example:

`python3 ./poipiku-dl.py -d '/mnt/tank/poipiku-archive/' -c '/home/lunaris/Desktop/poipiku-cookies.txt' -u 'https://poipiku.com/ID HERE/' -v True -t 10 -p 'answer'`
