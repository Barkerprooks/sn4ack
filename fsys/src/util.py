import os, ubinascii

def zfill(string, width):
    
    if len(string) < width:
        return ("0" * (width - len(string))) + string
    else:
        return string


def ip_range(dev_addr, netmask):

    try:
        ip_octets = [int(i) for i in dev_addr.split('.')]
        nm_octets = [int(i) for i in netmask.split('.')]
    except:
        print("not a valid ip address")
        return

    ip_binary = [zfill(bin(i).lstrip('0b'), 8) for i in ip_octets]
    nm_binary = [zfill(bin(i).lstrip('0b'), 8) for i in nm_octets]

    ip_mask = ''.join(ip_binary)
    submask = ''.join(nm_binary)

    zeros = submask.count("0")
    ones = 32 - zeros

    return abs(2 ** zeros - 2)


def random_mac(output_bytes=None):

    macinfo = {
        "bin": b'',
        "hex": []
    }
    
    for i in range(6):
        newbyte = os.urandom(1)
        macinfo["bin"] += newbyte.strip()
        macinfo["hex"].append(ubinascii.hexlify(newbyte))

    macinfo["hex"] = str(b':'.join(macinfo["hex"]))

    return macinfo
