import uhashlib, usocket, uos

import src.icmp as icmp
import src.portmap as portmap

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

    if required:
        out = "error: %s requires %d argument(s). %d given\r\n" % (cmd, required, len(args))
        print(out) 
        send_output(sock, out)

class ShellServer:

    def __init__(self, ifconfig):
        
        self.ifconfig = ifconfig
        self.authenticated = False

        with open("/home/.shrc", "rt") as fs:
            options = fs.read().split('\n')
            options = options[1:-1]
            for i in range(len(options)):
                options[i] = options[i].split('=')[1]

        self.username = options[0]
        self.hascolor = options[1]
       
        with open(options[2], "rb") as fs:
            self.greeting = fs.read()


    def _greet(self, connfd, info):
        onport = b"\r\n> login from [%s:%d]\r\n\r\n" % (info[0].encode("utf-8"), info[1])
        connfd.send(self.greeting + onport)


    def _handle(self, connfd):

        while True:
            
            if not self.authenticated:
                connfd.send(b"enter password: ") 
            else: 
                connfd.send(b"[%s] > " % self.username)
            
            msg = connfd.recv(1024)
            msg_parts = [i.decode("utf-8").strip() for i in msg.split(b' ')]

            print(msg_parts)

            cmd = msg_parts[0]
            args = None
            if len(msg_parts) > 0:
                args = msg_parts[1:]

            if cmd == "quit" or cmd == "exit":
                self._close(connfd)
                break

            if not self.authenticated:
                if not self._authenticate(cmd):
                    connfd.send(b"invalid password")
            else:
                execute(cmd, args, connfd, self.ifconfig)
    

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

    def _close(self, connfd):
        connfd.send(b"bye\r\n")
        connfd.close()
        execute("cd", ["/"])

    def start(self, port=1337):
        
        print("starting shell on port %d, press CTRL+C to stop it." % port)
        execute("cd", ["home"])
        
        sockfd = usocket.socket()
        sockfd.bind(("", port))
        sockfd.listen(1)
        
        try:
            connfd, connport = sockfd.accept()
        except:
            import sys
            sys.exit(0)
        
        self._greet(connfd, connport)
        self._handle(connfd)
