# poipiku-dl
A tool written in Python to download images from poipiku. Under early development. Tested on Windows and Linux. Should work on all OS-es


## Requirements
Some pip modules are needed for poipiku-dl to work. Some of them are already pre-installed on your system. Copy-paste this command and you should be good here:

`pip3 install requests termcolor urllib3 selenium`

You also need a webdriver, specifically the geckodriver for Firefox. You can download it here: https://github.com/mozilla/geckodriver/releases.

You also need Firefox on the system running the command. Geckodriver only hooks into Firefox, and is therefore dependent on having Firefox installed on your system. Don't worry, this runs headless. You will be able to run the script regardless of whether you have a GUI installed or not. You just need the Firefox binary.

| Command | OS |
| --- | --- |
| `sudo apt install firefox` | Ubuntu/Debian |
| `sudo pacman -S firefox` | Arch/Manjaro |
| `sudo dnf install firefox` | RHEL/Fedora/CentOS

## How to use
| Argument | Description |
| --- | --- |
| `-q` | Don't output to terminal |
| `-d PATH` | Specify output-directory |
| `-g PATH-TO-GECKODRIVER` | Specify path to geckodriver executable |
| `URL` **REQUIRED**| The only required argument. Specifies which link to look for images | 


For -d and -g, poipiku-dl.py will output to current directory and look for geckodriver in current directory. All arguments in brackets [] are optional.

`python3 .\poipiku.py [-q] [-d PATH] [-g PATH-TO-GECKODRIVER] 'enter URL here in quotes'`

### Example:

`python3 .\poipiku.py -q -d '/mnt/tank/poipiku-archive/' -g '/usr/bin/geckodriver' 'https://poipiku.com/ID HERE/'`
