import uos, usocket, ussl
import network

from src.fctl import f_or_d


def request(method, url, headers=None, data=None, sock=None, savetofile=False):

    if headers and isinstance(headers, dict) or data and isinstance(data, dict):
        print("dumbass")
        return None

    response = dict(code=-1, content='', headers=dict())
    resource, body = '/', ''
    
    if method.upper() != "GET" and method.upper() != "POST":
        out = "method %s not supported" % method.upper()
        print(out)
        if sock:
            sock.write(out.encode("utf-8"))
        return None
    
    port = 80
    if "https://" == url[:8]:
        port = 443
    elif "http://" != url[:7]:
        out = "stream wrapper format incorrect"
        print(out)
        if sock:
            sock.write(out.encode("utf-8"))
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
            out = "request format incorrect"
            print(out)
            if sock:
                sock.write(out.encode("utf-8"))
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

    info = usocket.getaddrinfo(host, port, 0, usocket.SOCK_STREAM)[0]
    sockfd = usocket.socket(info[0], info[1], info[2])
    sockfd.settimeout(5)
     
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
    
    try:
        response["code"] = int(status[9:12].decode("utf-8"))
    except ValueError:
        response["code"] = -1
        return None

    at_headers = True
    recv = 1


    while 1:
         
        if not recv or recv == b'':
            break
        
        try:
            recv = sockfd.readline()
        except OSError:
            break

        if at_headers:
            if recv == b'\r\n' or b':' not in recv:
                at_headers = False
                continue
            header = recv.decode("utf-8").split(": ")
            response["headers"][header[0]] = header[1]
        else:
            print(response["content"])
            response["content"] += recv.decode("utf-8")


    httpout = "status: %s\n\n%s\n\n%s\n\n" % (response["code"], response["headers"], response["content"])
    
    userout = "HOST: %s\nPORT: %s\nRESOURCE: %s\n\n" % (host, port, resource)
    if method.upper() == "POST":
        userout += "DATA:\n%s" % body
    
    print(userout)
    print(httpout)

    if sock:
        sock.write(userout.encode("utf-8"))
        sock.write(httpout.encode("utf-8"))

    if savetofile:
        lastn = 0
        fname = "%s-%s" % (method.upper(), host)

        try:
            uos.stat("/home/Documents/inet")
        except:
            uos.mkdir("/home/Documents/inet")

        for f in uos.listdir("/home/Documents/inet"):
            if fname in f:
                try:
                    num = int(f.split('_')[1].split('.')[0])
                    if num > lastn:
                        lastn = num
                except ValueError:
                    print("failed to save file")

        fname += "_%s.txt" % lastn
        fname = "/home/Documents/inet/" + fname

        with open(fname, "wt+") as fs:
            fs.write(userout)
            fs.write(httpout)

    return response

