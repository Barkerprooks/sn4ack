import uos, utime
import ntptime

from src.util import zfill

def f_or_d(fstat):
    if fstat == 32768:
        return "F"
    elif fstat == 16384:
        return "D"
    else:
        return "?"


def send_output(sock, output):
    if sock:
        if isinstance(output, str):
            output = output.encode("utf-8")
        sock.send(output + b"\r\n")


# ls
def list_dir(path=None, sock=None):
    try:
        if path:
            out = "%s: " % path
            print(out)
            send_output(sock, out)

            for fd in uos.ilistdir(path):
                out = "%s | %d bytes \t... %s" % (f_or_d(fd[1]), fd[3], fd[0])
                print(out)
                send_output(sock, out)
        else: 
            for fd in uos.ilistdir():
                out = "%s | %d bytes \t... %s" % (f_or_d(fd[1]), fd[3], fd[0])
                print(out)
                send_output(sock, out)
    except:
        out = "not a directory"
        print(out)
        send_output(sock, out)

# cd
def change_dir(path, sock=None):
    try:
        uos.chdir(path)
    except:
        out = "not a directory"
        print(out)
        send_output(sock, out)

# cat
def read_file(path, sock=None):
    try:
        with open(path, "rb") as fs:
            content = fs.read()
            print(content.decode("utf-8"))
            send_output(sock, content)
    except:
        out = "failed to open file"
        print(out)
        send_output(sock, out)

# more
def read_file_more(path, sock=None):
    
    lines_to_print = 40
    sections = []

    try:
        with open(path, "rt") as fs:
            content = fs.read()
    except:
        out = "failed to open file"
        print(out)
        send_output(sock, out)
        return

    output = ''
    line = ''
    lines = 0
    lnums = 0
    for char in content:

        if lines == lines_to_print:
            sections.append(output)
            output = ''
            lines = 0

        line += char
        
        if char == '\n':
            lnums += 1
            lines += 1
            output += str(lnums) + '\t' + line
            line = ''
                
    sections.append(output)

    for part in sections:
        print(part)
        if sock:
            sock.send(part.encode("utf-8"))
            sock.send(b"[press enter to continue]:")
            while True:
                cont = sock.recv(1024)
                if cont == b'\n' or cont == b'\r' or cont == b"\r\n":
                    break
        else:
            while True:
                cont = raw_input()
                if cont == b'\n' or cont == b'\r' or cont == b"\r\n":
                    break

# rm
def remove_file(path, sock=None):
    try:
        uos.remove(path)
    except:
        out = "could not remove %s" % path
        print(out)
        send_output(sock, out)


# mv
def move_fd(old_fd, new_fd, sock=None):
    try:
        uos.rename(old_fd, new_fd)
    except:
        out = "could not move %s" % old_fd
        print(out)
        send_output(sock, out)


# cp
def copy_fd(old_fd, new_fd, sock=None):
    try:
        with open(old_fd, "rt") as old_fs:
            with open(new_fd, "wt+") as new_fs:
                new_fs.write(old_fs.read())
    except:
        out = "could not move %s" % old_fd
        print(out)
        send_output(sock, out)
    

# cwd
def get_cwd(sock=None):
    cwd = uos.getcwd()
    print(cwd)
    send_output(sock, cwd)


# mkdir
def add_directory(directory, sock=None):
    try:
        uos.mkdir(directory)
    except:
        out = "could not create %s" % directory
        print(out)
        send_output(sock, out)


# rmdir
def del_directory(directory, sock=None):
    try:
        uos.rmdir(directory)
    except:
        out = "could not remove %s" % directory
        print(out)
        send_output(sock, out)


def get_time(sock=None):
    try:
        t = utime.localtime(ntptime.time())

        h = zfill(str(t[3]), 2)
        m = zfill(str(t[4]), 2)
        s = zfill(str(t[5]), 2)

        time = "%s:%s:%s GMT\r\n%s/%s/%s" % (h, m, s, t[1], t[2], t[0])
        print(time)
        send_output(sock, time)
    except:
        out = "could not get time"
        print(out)
        send_output(sock, out)


#TODO
# mount
def mount_fs(fs, directory, sock=None):
    pass

# umount
def unmount_fs(fs, directory, sock=None):
    pass


