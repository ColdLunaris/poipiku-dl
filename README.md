# poipiku-dl (CURRENTLY NOT WORKING!)
They changed how they handle cookies for logged in sessions, and the current version of this script does not work properly when not using cookies. Basically, the script isn't working in its current state. I'll try to work it out...

A tool written in Python to download images from poipiku. Under development. Tested on Windows and Linux. Should work on all OS's.

## Requirements
Some pip modules are needed for poipiku-dl to work. Some of them are already pre-installed on your system. Copy-paste this command and you should be good here:

`pip3 install requests termcolor urllib3 selenium`

If you still get an error for missing modules, that's when Google helps you out.

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
| `-c PATH-TO-COOKIES-FILE` | Specify path to cookies with Poipiku-login |
| `URL` **REQUIRED**| The only required argument. Specifies which link to look for images | 

For -d and -g, poipiku-dl.py will output to current directory and look for geckodriver in PATH if not specified. All arguments in brackets [] are optional.

`python3 .\poipiku.py [-q] [-d PATH] [-g PATH-TO-GECKODRIVER] [-c PATH-TO-COOKIES-FILE] 'enter URL here in quotes'`

### Use with cookie
Poipiku locks links for full-res images behind a login. You can supply already authenticated cookies by passing `-c` and specifying the txt-file. Use Export Cookies for Firefox, as it's the only one I've tested and know works. You're on your own if you choose not to. Get the extension here: https://addons.mozilla.org/en-US/firefox/addon/export-cookies-txt/. I've also only tested with a Twitter-login, so I don't know if any other forms of logins work.

### Example:

`python3 .\poipiku.py -q -d '/mnt/tank/poipiku-archive/' -g '/usr/bin/geckodriver' -c '/home/lunaris/Desktop/poipiku-cookies.txt' 'https://poipiku.com/ID HERE/'`
