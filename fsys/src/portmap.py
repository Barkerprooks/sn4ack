import usocket, uselect, utime

def scan_tcp_port(host, port, text=b"nice port ;)"):
    
    sockfd = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
    sockfd.setblocking(0)
    sockfd.settimeout(1)

    try:
        sockfd.connect((host, port))
        sockfd.close()
    except OSError:
        sockfd.close()
        return False

    return True

def scan_host(host, allport=False, sock=None):
    
    scanning = "scanning host %s" % host
    print(scanning)
    if sock:
        sock.send(scanning.encode("utf-8") + b"\r\n")

    portrange = 1000
    if allport:
        portrange = 2 ** 16

    for port in range(portrange):
        
        print(port)

        if port == portrange / 2:
            msg = "\t[~50% done]"
            print(msg)
            if sock:
                sock.send(msg.encode("utf-8") + b"\r\n")

        if scan_tcp_port(host, port):
            found = "\tport %d |\t open" % port
            print(found)
            if sock:
                sock.send(found.encode("utf-8") + b"\r\n")

def mass_scan(ip_list, sock=None):

    for ip in ip_list:
        scan_host(ip, sock)
