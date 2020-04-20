#!/usr/bin/env python3
# make sure your python version is >= 3.5

import serial
import glob, hashlib, os, platform, sys, subprocess, time


FLASH = "esptool.py"
FSCTL = "ampy"
UPYFW = "bin/esp32-idf3-20191220-v1.12.bin"


def lookup_ports() -> list:

    device_ports = []
    system_ports = glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*")
    
    if platform.system() == "Windows":
        system_ports = ["COM%s" % i for i in range(0, 255)]

    for port in system_ports:
        try:
            test = serial.Serial(port, 115200)
            if test.is_open:
                device_ports.append(port)
            test.close()
        except (serial.serialutil.SerialException, PermissionError):
            print("Permission to USB ports was denied.")
            if platform.system() == "Linux":
                print('try: "sudo python %s"' % sys.argv[0])
            sys.exit(1)

    return device_ports


def check_firmware(port) -> bool:

    print("checking if firmware is installed")

    try:
        if subprocess.run([FSCTL, "-p", port, "reset"], timeout=10).returncode != 0:
            check_firmware(port)
        else:
            return True
    except subprocess.TimeoutExpired:
        return False


def flash_firmware(port):
    
    erase = subprocess.run([FLASH, "-p", port, "erase_flash"]).returncode
    if erase == 0:
        subprocess.run([FLASH, "-p", port, "--after", "hard_reset", "write_flash", "0x1000", UPYFW])

    try:
        subprocess.run([FSCTL, "-p", port, "reset"], timeout=10)
    except:
        print("Failed to reset device, please disconnect then reconnect your esp32.")
        input("[press enter to continue]")

def walk_fs(start):

    fs = {
        "files": [],
        "bdirs": [],
        "sdirs": []
    }

    for fd in os.listdir(start):
        full = start + '/' + fd
        if os.path.isfile(full):
            fs["files"].append(fd)
        elif os.path.isdir(full):
            fs["bdirs"].append(fd)
            recurse = walk_fs(full)
            for f in recurse["files"]:
                fs["files"].append(fd + '/' + f)
            for d in recurse["bdirs"]:
                fs["sdirs"].append(fd + '/' + d)

    return fs 

def install_system(port):
    
    print("setup networking (leave password blank if none):")

    if not os.path.isfile("fsys/etc/wlan/wlan.conf"):

        if not os.path.isdir("fsys/etc/wlan"):
            os.mkdir("fsys/etc/wlan")

        net_ssid = input("network ssid: ")
        password = input("passphrase: ")
        creds = [net_ssid, password]

        with open("fsys/etc/wlan/wlan.conf", "wt+") as fs:
            fs.write('\n'.join(creds))
    else:
        
        with open("fsys/etc/wlan/wlan.conf", "rt") as fs:
            creds = fs.read().split('\n')

        print("network creds exist, using: %s" % (creds[0]))

    print("setup system password: ")
    
    if not os.path.isfile("fsys/etc/passwd"):
        
        while True:
            passwd = input("password: ")
            checkp = input("confirm: ")

            if checkp == passwd:
                print("installing system...")

                hashwd = hashlib.sha256(passwd.encode("utf-8"))
                with open("fsys/etc/passwd", "wb+") as fs:
                    fs.write(hashwd.digest())

                break
            else:
                print("passwords do not match")
        
    else:
        print("password exists, installing system...")

    print("making sure device is clean")
    subprocess.run([FSCTL, "-p", port, "run", "utils/nukefs.py"]) 
    filesystem = walk_fs("fsys")

    swp = None
    for i in range(len(filesystem["files"])):
        if filesystem["files"][i] == "boot.py":
            swp = i

    if swp:
        temp = filesystem["files"][-1]
        filesystem["files"][-1] = filesystem["files"][swp]
        filesystem["files"][swp] = temp

    print(filesystem["files"])

    for d in filesystem["bdirs"]:
        success = None
        while success != 0:
             success = subprocess.run([FSCTL, "-p", port, "mkdir", d], timeout=7).returncode
        print("created %s" % d)
    
    for d in filesystem["sdirs"]:
        success = None
        while success != 0:
            success = subprocess.run([FSCTL, "-p", port, "mkdir", d], timeout=7).returncode
        print("created %s" % d)
   
    for f in filesystem["files"]:
        success = None
        location = "fsys/" + f
        while success != 0:
            try:
                subprocess.run([FSCTL, "-p", port, "reset"])
                success = subprocess.run([FSCTL, "-p", port, "put", location, f], timeout=15, capture_output=True).returncode
            except KeyboardInterrupt:
                sys.exit(0)
            except:
                print("trying again")
                success = None
        
        print("uploaded %s" % f)

    os.remove("fsys/etc/passwd")
    os.remove("fsys/etc/wlan/wlan.conf")

    return subprocess.run([FSCTL, "-p", port, "ls"], capture_output=True).stdout.decode("utf-8")


if __name__ == "__main__":

    ports = lookup_ports()
    selection = None

    if len(ports) == 0:
        print("No devices detected")
        sys.exit(1)

    for i in range(0, len(ports)):
        print("[%d] - %s" % (i, ports[i]))
    
    while not isinstance(selection, int):
        selection = input("select USB port from list (enter number): ")
        try:
            selection = int(selection)
        except:
            print("not a valid index")

    port = ports[selection]

    if not check_firmware(port):
        flash_firmware(port)

    fs = install_system(port)

    print("\nFILESYSTEM UPLOADED:\n%s" % fs)
    subprocess.run([FSCTL, "-p", port, "run", "utils/getip.py"])

    print("\npress RST button, wait a bit, and connect to shell on port 22")
