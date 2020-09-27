# poipiku-dl
A tool written in Python to download images from poipiku. Under early development. Tested on Windows. Should work on all OS-es


## Requirements
Some pip modules are needed for poipiku-dl to work. Some of them are already pre-installed on your system. Copy-paste this command and you should be good here:

`pip3 install requests termcolor urllib3 selenium`


You also need a webdriver, specifically the geckodriver for Firefox. You can download it here: https://github.com/mozilla/geckodriver/releases. Put this in the same folder as poipiku-dl.py.

## How to use

`python3 .\poipiku.py 'enter URL here in quotes'`

There are no arguments yet. I will however add some later, like specifying save-location, location of geckodriver, quiet-mode etc.
