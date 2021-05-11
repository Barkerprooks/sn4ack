# Sn4ack DEPRECIATED, SEE [VIPER OS](https://github.com/Barkerprooks/viper-os)
## V0.2 - INDEV
Sn4ack (snhack... as in snack) is an embeded hacking OS/shell made for the ESP32 microprocessor.\
The shell roughly emulates a unix environment through a tiny python interpreter called [Micropython](https://micropython.org).

### Requirements
- Python 3
- Pip for Python3

### Commands to install on Linux
```
1. git clone https://github.com/Barkerprooks/sn4ack.git
2. cd sn4ack
3. python -m venv env
4. source env/bin/activate
5. sudo python install.py
```
### How to use
1. Find the device on your network.
 - If the router supports Bonjour/MDNS the host name will be "snhack.local"
 - If not, the install script gives you the IP address
2. Use telnet or netcat to connect on port 22.
3. Have fun!

#### Commands Available
```
Basic:
- ls / dir 	... list files in directory
- cd / chdir 	... change working directory
- rm / del 	... delete a file
- cat 		... read a file
- more 		... read a file in chunks (buggy and slow for now)
- cp / copy 	... copy a file to a new location
- mv / move 	... move a file to a new location
- mkdir		... create a new empty directory
- date / time	... prints the date and time

Fun:
- ping 			... send icmp ping packets to a host
- icmp-scan 		... discover all hosts on a network
- pmap / nmap		... discover open TCP ports on a host
- http (GET|POST) <url> ... send an HTTP(S) request to a host
```
