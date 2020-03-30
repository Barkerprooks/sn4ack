import uctypes, urandom, uselect, usocket, ustruct, utime
import src.util


def icmp_packet(size):

    assert size >= 16, "packet too small"

    packet = b'Q' * size
    packet_info_t = {
            "type": uctypes.UINT8 | 0,
            "code": uctypes.UINT8 | 1,
            "checksum": uctypes.UINT16 | 2,
            "id": uctypes.UINT16 | 4,
            "seq": uctypes.INT16 | 6,
            "timestamp": uctypes.UINT64 | 8
    }

    header = uctypes.struct(
            uctypes.addressof(packet), 
            packet_info_t, 
            uctypes.BIG_ENDIAN
    )

    header.type = 8
    header.code = 0
    header.checksum = 0
    header.id = urandom.randint(0, 65535)
    header.seq = 1
    
    return [ header, packet, packet_info_t ]


def checksum(data):

    if len(data) & 0x1:
        data += b'\0'
    
    check = 0
    
    for pos in range(0, len(data), 2):
        byte1 = data[pos]
        byte2 = data[pos + 1]
        check += (byte1 << 8) + byte2
    
    while check >= 0x10000:
        check = (check & 0xffff) + (check >> 16)
    
    return (~check & 0xffff)


def scan(ifconfig, sock=None):

    starting = "starting host discovery"
    print(starting)
    if sock:
        sock.send(starting.encode("utf-8") + b"\r\n")

    ip_list = []
    scanned = []

    address = ifconfig[0]
    netmask = ifconfig[1]
    gateway = ifconfig[2]

    scan_ip_prefix = gateway.split('.')[:3]
    scan_ip = '.'.join(scan_ip_prefix) + '.0'

    for count in range(util.ip_range(address, netmask)):
        
        if ping(scan_ip, repeat=10, timeout=100, silent=True):
            print(scan_ip)
            if sock:
                sock.send(scan_ip.encode("utf-8") + b"\r\n")

        scan_ip_octets = [int(i) for i in scan_ip.split('.')]

        if scan_ip_octets[3] == 225:
            scan_ip_octets[2] += 1
            scan_ip_octets[3] = 0
        elif scan_ip_octets[2] == 225:
            break
        else:
            scan_ip_octets[3] += 1

        scan_ip_octets = [str(i) for i in scan_ip_octets]
        scan_ip = '.'.join(scan_ip_octets)


def ping(address, repeat=5, interval=10, timeout=3000, size=64, silent=False, sock=None):

    host = usocket.getaddrinfo(address, 1)[0][-1][0]
    icmp = icmp_packet(size)

    sockfd = usocket.socket(usocket.AF_INET, usocket.SOCK_RAW, 1)
    sockfd.setblocking(0)
    sockfd.settimeout(timeout / 1000)
    sockfd.connect((host, 1))

    if not silent:
        pinging = "PING: %s" % host
        print(pinging)
        if sock:
            sock.send(pinging.encode("utf-8") + b"\r\n")

    seqs = list(range(1, repeat + 1))
    
    c = 1
    t = 0
    transmitted = 0
    recieved = 0

    complete = False
    
    while t < timeout:
        
        if t == interval and c <= repeat:
            icmp[0].checksum = 0
            icmp[0].seq = c
            icmp[0].timestamp = utime.ticks_us()
            
            icmp[0].checksum = checksum(icmp[1])

            if sockfd.send(icmp[1]) == size:
                transmitted += 1
                t = 0
            else:
                seqs.remove(c)
            c += 1

        while not complete:

            sockets, _, _ = uselect.select([sockfd], [], [], 0)
            
            if sockets:
                response = sockets[0].recv(4069)
                rpointer = memoryview(response)

                rheader = uctypes.struct(
                        uctypes.addressof(rpointer[20:]), 
                        icmp[2],
                        uctypes.BIG_ENDIAN
                )

                seq = rheader.seq

                if rheader.type == 0 and rheader.id == icmp[0].id and (seq in seqs):
                    
                    elapsed = (utime.ticks_us() - rheader.timestamp) / 1000
                    ttl = ustruct.unpack('>B', rpointer[8:9])[0]
                    recieved += 1

                    if not silent:
                        s = seq
                        l = len(response)
                        pong = "PONG - %d: %u bytes | ttl: %u (%f ms)" % (s,l,ttl,elapsed)
                        print(pong)
                        if sock:
                            sock.send(pong.encode("utf-8") + b"\r\n")

                    seqs.remove(seq)
                    if len(seqs) <= 0:
                        complete = True
            else:
                break

        utime.sleep_ms(1)
        t += 1

    sockfd.close()
    return recieved

# special thanks to Shawwwn on github for the python wizardry https://gist.github.com/shawwwn/91cc8979e33e82af6d99ec34c38195fb


