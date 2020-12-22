import network
import utime
import select
import esp

import src.shell as shell
import src.util as util

import lib.slimDNS as mdns

from machine import Pin

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


esp.osdebug(None)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

#randomize_mac(wlan)

with open("etc/wlan/wlan.conf", "rt") as fs:
    config = fs.read()
    config = config.split('\n')
    wlan.connect(config[0], config[1])

print("trying to connect to the internet...")
while not wlan.isconnected():
    pass

ifconfig = wlan.ifconfig()
print("connected. you are %s" % ifconfig[0])

led = Pin(2, Pin.OUT)
led.value(1)

sh = shell.ShellServer(ifconfig=ifconfig)
dns = mdns.SlimDNSServer(ifconfig[0], "snhack")

sh.start(22)

while True:
    
    led.value(0)
    sockets, _, _ = select.select([sh.socket, dns.sock], [], [])

    if sh.socket in sockets:
        
        led.value(1)
        sh._handle()

    if dns.sock in sockets:
        print("recv")
        dns.process_waiting_packets()
