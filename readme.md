# Sn4ack

## V0.2 - INDEV
Sn4ack (snhack... as in snack) is an embeded hacking shell made for the ESP32 microprocessor.\
The shell roughly emulates a unix environment through a tiny python interpreter called [Micropython](https://micropython.org).

### How to install
1. clone this repository and cd into it
2. plug in your ESP32 device
3. run "python install.py"
 - note: if running on linux as a non root user, you may have to use sudo.
```
git clone https://github.com/Barkerprooks/sn4ack.git
cd sn4ack
python install.py
```
### How to use
1. Find the device on your network
 - If the router supports Bonjour/MDNS the host name will be "snhack.local"
 - If not, the install script gives you the IP address
2. Use telnet or netcat to connect on port 22
3. Have fun!
