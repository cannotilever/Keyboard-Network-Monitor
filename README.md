# Keybord-Network-Monitor
Python Scripts to monitor and control elements of your network from a compatible Logitech RGB keyboard

## Important:

- Currently, desktop.py (the program that controls the keyboard) only works on a linux host
- All credit for controling the lighting on the keyboard goes to [MatMoul](https://github.com/MatMoul/g810-led)
    - In order for this script to work, ensure that g810-led is installed and in your PATH
- For hotkeys to work, the script must be executed with root privilidges
- desktop.py runs slowly intentionally to reduce its CPU footprint, you can change this by modifying the time.sleep()'s but default values work fine.

## Usage:

Note: these hotkeys work no matter which program is in focus.

To select a host to monitor, press shift + its corresponding F key, or shift+esc for localhost. When monitoring a host, keys q-p represent CPU usage, a-; represent RAM usage, and z-/ represent disk usage of the partition mounted at /. 

To shutdown or reboot the selected host, press ctrl+num5 and the number pad should start flashing in an X pattern. This pattern means that the power control keys are 'armed' and will be active for about 10 seconds. Once armed, press ctrl+home to reboot and ctrl+end to poweroff the remote host.

If the keyboard flashes red when you select a host for monitoring, either the host is marked as 'other' or the server program cannot be reached. To return to the default view, press esc with no other modifiers. 

## Installation:

- desktop.py
    - Linux Hosts:
        - follow the instructions to install [g810-led](https://github.com/MatMoul/g810-led/blob/master/INSTALL.md), ensure that it is in PATH
        - ensure python3 and python3-pip are installed and execute `pip3 install keyboard psutil` as root
        - download desktop.py and KeyNetMon_desktop.service
        - open desktop.py with your favorite editor and add any hosts that you would like to monitor starting at line 198, following the examples there.
        - `chmod +x desktop.py`
        - `mv desktop.py /usr/bin/`
        - `mv KeyNetMon_desktop.service /etc/systemd/system/`
        - `systemctl enable KeyNetMon_desktop.service`
        - `systemctl start KeyNetMon_desktop.service`
        - At this point, your keyboard should have turned blue and your F keys should be lighting up either green or red.

    - Windows Hosts:
        - Coming Soon
    
- server.py
    - ensure python3 and python3-pip are installed and execute `pip3 install psutil` as root
    - download server.py and KeyNetMon_server.service
    - `chmod +x server.py`
    - `mv server.py /usr/bin/`
    - For systems with systemd
        - `mv KeyNetMon_desktop.service /etc/systemd/system/`
        - `systemctl enable KeyNetMon_server.service`
        - `systemctl start KeyNetMon_server.service`
    - For systems without systemd
        - make the program autostart, I believe in you
        - I don't currently have a non-systemd system to test with
    
## Compatability:

So far, desktop.py has been tested on Ubuntu 20.04 LTS with a logitech G810 but should work on nearly all linux. Also, server.py has been tested on Proxmox VE 6.1, Ubuntu server 20.04 LTS, and Fedora Server Edition 32 but should work on anything that can run python and pip3, although shutdown and reboot won't currently work on Windows hosts.

## Next Steps:

The most immediate development priority is bringing Windows support using the logiPy library for keyboard lighting control. Next in priority is an interactive setup process that stores configs in a separate file so that manually adding points via altering the code is no longer necessary. Finally, I know that doing os.system calls to set lighting is not great, so in the future I hope to integrate with g810-led's C++ library as to not make os.system calls.