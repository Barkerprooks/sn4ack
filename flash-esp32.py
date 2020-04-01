#!/usr/bin/env python3
#3/31/2020 - parker

import os, subprocess, time

UPYBIN_PATH = "bin/esp32-idf3-20191220-v1.12.bin"
NTCONF_PATH = "fsys/etc/wlan/wlan.conf"


device = input("device port (COM* or /dev/tty*): ")
subprocess.call(["esptool.py", "-p", device, "erase_flash"])
subprocess.call(["esptool.py", "-p", device, "write_flash", "-z", "0x1000", UPYBIN_PATH])

time.sleep(1.0)
subprocess.call(["ampy", "-p", device, "reset"])

if not os.path.isfile(NTCONF_PATH):

    ntssid = input("network ssid: ")
    ntpass = input("network passphrase (blank if none): ")
    ntcreds = [ntssid, ntpass]
    
    with open(NTCONF_PATH, 'wt+') as fs:
        fs.write('\n'.join(ntcreds))

else:
    print("clearing filesystem")
    subprocess.call(["ampy", "-p", device, "run", "utils/nuke.py"])


for fd in os.listdir("fsys"):
    full = "fsys/" + fd
    subprocess.call(["ampy", "-p", device, "put", full, fd])
    time.sleep(0.5)
    print("uploaded: %s" % fd)

print("press RST button or unplug device to use.")
