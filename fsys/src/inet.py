import usocket
import network

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("Baird-2G", "bluetrain222")
while not wlan.isconnected():
    pass


def request(method, url, header=None, data=None, savetofile=False):

    if header and not isinstance(header, dict):
        print("header must be a dict")
        return None
    
    if data and not isinstance(data, dict):
        print("data must be a dict")
        return None
    
    response = {
        "headers": {},
        "content": '',
        "status": -1,
    }
    
    if method.upper() != "GET" and method.upper() != "POST":
        print("incorrect method")
        return None
    
    port = 80
    if "https://" == url[:8]:
        port = 443
    elif "http://" != url[:7]:
        print("stream wrapper format incorrect")
        return None

    resource = ''
    host = url.split("//")[1]
    if '/' in host:
        elements = host.split('/')
        resource = elements[1]
        host = elements[0]

    if ':' in host:
        elements = host.split(':')
        try:
            host = elements[0]
            port = int(elements[1])
        except:
            print("request format incorrect")
            return None

    if data and '?' not in resource and method.upper() == "GET":
        resource += '?'
        for key in data:
            data

    print("%s %s" % (host, port))

    info = usocket.getaddrinfo(host, port, 0, usocket.SOCK_STREAM)[0]
    sockfd = usocket.socket(info[0], info[1], info[2])

    if port == 443:
        sockfd = ussl.wrap_socket(sockfd, host)
    
    sockfd.connect((host, port))

    sockfd.send(b"%s /%s HTTP/1.1\r\n" % (method.upper(), resource))
    sockfd.send(b"Host: %s\r\n" % host)

    sockfd.send(b"\r\n")

    status = sockfd.readline()
    print(status)

    headers = True
    while 1:
        recv = sockfd.readline()
        if not recv:
            break
        
        if headers:
            if recv == b'\r\n':
                headers = None
            header = recv.decode("utf-8").split(": ")
            print(header)
            response["headers"][header[0]] = header[1]
        else:
            response["content"] += recv.decode("utf-8")

    print(response)
    return response


def get(url, header=None, data=None):
    request("get", url, header=header, data=data)

request("get", "http://192.168.1.27")
