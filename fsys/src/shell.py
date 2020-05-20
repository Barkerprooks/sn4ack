import uhashlib, usocket, uos, utime
import ntptime

import src.icmp as icmp
import src.pmap as portmap
import src.inet as inet

from src.fctl import *

CMDLIST = {
    "list files": ["ls", "dir"],
    "change directory": ["cd", "chdir"],
    "delete file": ["rm", "del"],
    "read files": ["cat", "less", "more"],
    "copy files": ["cp", "copy"],
    "move files": ["mv", "move"],
    "create directory": ["mkdir"],
    "delete directoty": ["rmdir"],
    "icmp ping a host": ["ping"],
    "icmp scan network": ["icmp-scan", "show-hosts"],
    "send http(s) requests": ["http (GET|POST) <URL>"],
    "port map a host": ["pmap", "nmap", "portmap"] 
}

def show_available_commands(sock=None):
    
    commands = "commands:\n"

    for key in CMDLIST:
        commands += '\n\t'
        cmds = CMDLIST[key]
        for i in range(len(cmds)):
            commands += "%s" % cmds[i]
            if i < len(cmds) - 1:
                commands += ','
        commands += " \t-- %s" % key

    return commands + '\n'

def execute(cmd, args=None, sock=None, config=[]):

    required = 0

    if cmd == "help" or cmd == "?":
        if args:
            out = "not impl yet"
            print(out)
            send_output(sock, out)
        else:
            commands = show_available_commands(sock=sock)
            print(commands)
            send_output(commands)

    elif cmd == "ls" or cmd == "dir":
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

    elif cmd == "icmp-scan" or cmd == "host-scan":
        icmp.scan(config, sock=sock)

    elif cmd == "portmap" or cmd == "nmap" or cmd == "pmap":
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

    elif cmd == "http" or cmd == "curl":
        if args:

            url = args[len(args) - 1] # url will always be last
            method = args[0]
            
            headers = None
            data = None
            
            save = False

            if len(args) > 2:
                opts = args[1:len(args) - 2]
                
                if "-s" or "--save" in opts:
                    save = True
                    
                for i in range(len(opts)):
                    
                    quote = ['"', "'"]
                    
                    if opts[i] == "-h" or opts[i] == "--headers":

                        try:
                            opt = opts[i+1]
                        except:
                            out = "missing header"
                            print(out)
                            send_output(sock, out)
                        
                        start = opt[0]
                        end = opts[len(opt) - 1]
                        header_list = []

                        if start in quote and end in quote and start == end:
                            header_list = opt.split(',')
                        else:
                            header_list = opt.split(',')
                            for j in range(len(header_list)):
                                header_list[j] = header_list[j].strip()
                        
                        headers = dict()
                        for h in header_list:
                            keyval = h.split(':')
                            headers[keyval[0]] = keyval[1]
                    
                    elif opts[i] == "-d" or opts[i] == "--data":

                        try:
                            opt = opts[i+1]
                        except:
                            out = "missing data"
                            print(out)
                            send_output(sock, out)

                        start = opt[0]
                        end = opt[len(opt) - 1]
                        data_list = []
                        
                        if start in quote and end in quote and start == end:
                            data_list = opt.split(',')
                        else:
                            data_list = opt.split(',')
                            for j in range(len(data_list)):
                                data_list[j] = data_list[j].strip()
            
                        data = dict()
                        for d in data_list:
                            keyval = d.split('=')
                            data[keyval[0]] = keyval[1]

            inet.request(method, url, headers=headers, data=data, sock=sock, savetofile=save)
            
        else:
            required = 1

    if required:
        out = "error: %s requires at least %d argument(s). %d given\r\n" % (cmd, required, len(args))
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
        import machine
        machine.reset()


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
