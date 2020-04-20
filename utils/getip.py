import network
import uos

print("getting device ip")

try:
    
    with open("/etc/wlan/wlan.conf", "rt") as fs:
        credinfo = fs.read().split('\n')
    
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(credinfo[0], credinfo[1])

    while not wifi.isconnected():
        pass

    print(wifi.ifconfig()[0])

except:

    print("no networking info")
