import uos, usocket, ussl
import network

from src.fctl import f_or_d

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
# oops
wlan.connect("Baird-2G", "<censored>")
while not wlan.isconnected():
    pass


def request(method, url, headers=None, data=None, savetofile=False):

    if headers and not isinstance(headers, dict):
        print("headers must be in a dict")
        return None
    
    if data and not isinstance(data, dict):
        print("data must be in a dict")
        return None

    response = dict(code=-1, content='', headers=dict())
    resource, body = '/', ''
    
    if method.upper() != "GET" and method.upper() != "POST":
        print("method %s not supported" % method.upper())
        return None
    
    port = 80
    if "https://" == url[:8]:
        port = 443
    elif "http://" != url[:7]:
        print("stream wrapper format incorrect")
        return None

    host = url.split("//")[1]

    if host[-1] == '/':
        host = host[:-1]
    
    if '/' in host:
        elements = host.split('/')
        resource = '/'.join(elements[1:])
        host = elements[0]

    if ':' in host:
        elements = host.split(':')
        try:
            host = elements[0]
            port = int(elements[1])
        except:
            print("request format incorrect")
            return None

    if data:
        if method.upper() == "GET":
            resource += '?'
            for key in data:
                resource += key + "=" + data[key] + "&"

        elif method.upper() == "POST":
            for key in data:
                body += key + "=" + data[key] + '&'
        
        resource = resource[:-1]

    print("REQUEST")
    print("raddress: %s:%s" % (host, port))
    print("resource: %s" % resource)
    if method.upper() == "POST":
        print("postbody: \n%s" % body)

    info = usocket.getaddrinfo(host, port, 0, usocket.SOCK_STREAM)[0]
    sockfd = usocket.socket(info[0], info[1], info[2])
    
    sockfd.connect((host, port))
    if port == 443:
        sockfd = ussl.wrap_socket(sockfd, server_hostname=host)

    sockfd.write(b"%s /%s HTTP/1.1\r\n" % (method.upper(), resource))
    sockfd.write(b"Host: %s\r\n" % host)

    if headers:
        for key in headers:
            sockfd.write(b"%s: %s\r\n" % (key, headers[key]))

    sockfd.write(b"\r\n")

    status = sockfd.readline()
    
    print("got here")

    try:
        response["code"] = int(status[9:12].decode("utf-8"))
    except ValueError:
        response["status"] = -1

    at_headers = True
    
    while 1:
        recv = sockfd.readline()
        
        if not recv:
            break
        
        if at_headers:
            if recv == b'\r\n' or b':' not in recv:
                at_headers = False
                continue
            header = recv.decode("utf-8").split(": ")
            response["headers"][header[0]] = header[1]
        else: 
            response["content"] += recv.decode("utf-8")

    print(response["headers"])
    print(response["content"])

    if savetofile:
        
        fname = "inet-%s.txt" % host

        for f in uos.listdir("var/inet"):
            if f == fname and len(f.split('.')) > 1:

        with open("inet-%s.txt" % host)

    return response


def get(url, header=None, data=None):
    request("get", url, header=header, data=data)


def post(url, header=None, data=None):
    request("post", url, header=header, data=data)


if __name__ == "__main__":

    request("get", "https://google.com/", savetofile=True)
