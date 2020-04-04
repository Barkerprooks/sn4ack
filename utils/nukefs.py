import uos

depth = 0

def exp():
   
    global depth

    for fd in uos.listdir():
        try:
            uos.remove(fd)
            print(('--' * depth) + "rm %s" % fd)
        except:
            print(('--' * depth) + "> %s" % fd)
            depth += 1
            uos.chdir(fd)
            exp()
            uos.chdir("..")
            depth -= 1
            uos.rmdir(fd)
            print(('--' * depth) + "rmdir %s" % fd)

exp()
