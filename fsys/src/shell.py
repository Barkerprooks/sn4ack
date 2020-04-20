import uhashlib, usocket, uos, utime
import ntptime

import src.icmp as icmp
import src.pmap as portmap

from src.fctl import *

def execute(cmd, args=None, sock=None, config=[]):

    required = 0

    if cmd == "ls" or cmd == "dir":
        if args:
            for arg in args:
                list_dir(arg, sock=sock)
        else:
            list_dir(sock=sock)
    
    elif cmd == "cd" or cmd == "chdir":
        if len(args) == 1:
            change_dir(args[0])
        else:
            required = 1
    
    elif cmd == "rm" or cmd == "del":
        if len(args) == 1:
            remove_file(args[0])
        else:
            required = 1

    elif cmd == "cat":
        if args:
            for arg in args:
                read_file(arg, sock=sock)
        else:
            required = 1
   
    elif cmd == "more":
        if len(args) == 1:
            read_file_more(args[0], sock=sock)
        else:
            required = 1

    elif cmd == "cp" or cmd == "copy":
        if len(args) == 2:
            copy_fd(args[0], args[1])
        else:
            required = 2
    
    elif cmd == "mv" or cmd == "move":
        if len(args) == 2:
            copy_fd(args[0], args[1])
        else:
            required = 2

    elif cmd == "mkdir":
        if len(args) == 1:
            add_directory(args[0], sock=sock)
        else:
            required = 1

    elif cmd == "rmdir":
        if args:
            for arg in args:
                del_directory(arg) 
        else:
            required = 1

    elif cmd == "ping":
        if args:
            for arg in args:
                icmp.ping(arg, sock=sock)
        else:
            required = 1

    elif cmd == "show yourselves" or cmd == "icmp-scan":
        icmp.scan(config, sock=sock)

    elif cmd == "portmap" or cmd == "nmap":
        if args:
            if args[0] == "all":
                if args[1]:
                    portmap.scan_host(args[1], allport=True, sock=sock)
                else:
                    required = 1
            else:
                portmap.scan_host(args[0], sock=sock)
        else:
            required = 1

    elif cmd == "date" or cmd == "time" or cmd == "datetime":
        get_time(sock=sock)

    if required:
        out = "error: %s requires %d argument(s). %d given\r\n" % (cmd, required, len(args))
        print(out) 
        send_output(sock, out)


class ShellServer:

    def __init__(self, ifconfig):
        
        self.ifconfig = ifconfig
        self.authenticated = False

        with open("/etc/sh/sh.conf", "rt") as fs:
            options = fs.read().split('\n')
            for i in range(len(options)):
                if '=' in options[i]:
                    options[i] = options[i].split('=')[1]

        self.username = options[0]
      
        with open(options[1], "rb") as fs:
            self.last_login = fs.read()
        
        with open(options[1], "wb") as fs:
            fs.write(self._time().encode("utf-8")) 

        with open("/etc/fs/version", "rb") as fs:
            self.version = fs.read()


    def _time(self):
        t = utime.localtime(ntptime.time())
        return "%s:%s:%s %s/%s/%s" % (t[3],t[4],t[5], t[1],t[2],t[0])


    def _greet(self):
        verstr = b"SN4ACK v%s" % self.version
        border = b'-' * (len(verstr) - 1) + b"\r\n"
        self.socket.send(border + verstr + border + b"\r\n\r\n")

        self.socket.send(b"current gmt time: %s\r\n" % self._time())
        self.socket.send(b"last login on: %s\r\n\r\n" % self.last_login)

        from_ip = "%s:%d" % (self.onport[0], self.onport[1])
        self.socket.send(b"login from [%s]\r\n" % (from_ip))


    def _handle(self):
        
        msg = self.socket.recv(1024)
        msg_parts = [i.decode("utf-8").strip() for i in msg.split(b' ')]

        print(msg_parts)

        cmd = msg_parts[0]
        args = None
        if len(msg_parts) > 0:
            args = msg_parts[1:]

        if cmd == "quit" or cmd == "exit":
            self._close()
            return

        if not self.authenticated:
            if not self._authenticate(cmd):
                self.socket.send(b"invalid password\r\n")
                self.socket.send(b"enter password: ") 
            else:
                self._greet()
                self.socket.send(b"[%s] > " % self.username)
        else:
            execute(cmd, args, self.socket, self.ifconfig)
            self.socket.send(b"[%s] > " % self.username)
    

    def _authenticate(self, passwd):
        
        hashwd = uhashlib.sha256(passwd.encode("utf-8")).digest()
        with open("/etc/passwd", "rb") as fs:
            checkwd = fs.read()
            print("orig: %s vs input: %s" % (checkwd, hashwd))
            if checkwd == hashwd:
                self.authenticated = True
                return True
            else:
                return False


    def _close(self):
        self.socket.send(b"bye\r\n")
        self.socket.close()
        execute("cd", ["/"])


    def start(self, port=1337):
        
        print("starting shell on port %d, press CTRL+C to stop it." % port)
        execute("cd", ["home"])
        
        sockfd = usocket.socket()
        sockfd.bind(("", port))
        sockfd.listen(1)
        
        try:
            self.socket, self.onport = sockfd.accept()
        except:
            import sys
            sys.exit(0)
        
        self.socket.send(b"enter password: ") 
        self._handle()
