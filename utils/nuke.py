import uos

def exp():
    
    for fd in uos.listdir():
        try:
            print("del %s" % fd)
            uos.remove(fd)
        except:
            print("going into %s" % fd)
            uos.chdir(fd)
            exp()
            uos.chdir("..")
            print("del %s" % fd)
            uos.rmdir(fd)
