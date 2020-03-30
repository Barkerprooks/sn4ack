import network
import ubinascii

import src.shell as shell
import src.util as util

def randomize_mac(iface):
    
    if not iface.active():
        iface.active(True)

    mac = util.random_mac()

    print("Your MAC address is: %s" % mac)

    try:
        iface.config(mac=mac["bin"])
        return mac
    except:
        randomize_mac(iface)


wlan = network.WLAN(network.STA_IF)
wlan.active(True)

randomize_mac(wlan)

with open("etc/wlan/wlan.conf", "rt") as fs:
    config = fs.read()
    config = config.split('\n')
    wlan.connect(config[0], config[1])

while not wlan.isconnected():
    pass

sh = shell.ShellServer(ifconfig=wlan.ifconfig())
sh.start(22)
