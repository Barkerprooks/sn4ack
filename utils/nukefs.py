import uos

depth = 0

def exp():
   
    global depth

    for fd in uos.listdir():
        try:
            uos.remove(fd)
            print(('\t' * depth) + "rm %s" % fd)
        except:
            print(('\t' * depth) + "> %s" % fd)
            depth += 1
            uos.chdir(fd)
            exp()
            uos.chdir("..")
            depth -= 1
            uos.rmdir(fd)
            print(('\t' * depth) + "rmdir %s" % fd)

exp()
