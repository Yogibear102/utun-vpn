import os
import fcntl
import socket
import select
import struct

def create_utun():
    # On macOS, /dev/tun doesn't work; we use utun devices via socket ioctl
    TUN_PATH = "/dev/"  # just for notation
    TUN_NAME = "utun2"  # macOS assigns name after open()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 443))
    print("[+] Connected to VPN server")

    # macOS-specific ioctl to create utunX
    utun_fd = open_utun()

    while True:
        r, _, _ = select.select([utun_fd, sock], [], [])
        if utun_fd in r:
            data = os.read(utun_fd, 1500)
            sock.sendall(data)
        if sock in r:
            data = sock.recv(1500)
            if not data:
                break
            os.write(utun_fd, data)

def open_utun():
    import ctypes, fcntl

    UTUN_CONTROL_NAME = b"com.apple.net.utun_control"
    AF_SYS_CONTROL = 2
    SYSPROTO_CONTROL = 2
    UTUN_OPT_IFNAME = 2

    class ctl_info(ctypes.Structure):
        _fields_ = [("ctl_id", ctypes.c_uint32),
                    ("ctl_name", ctypes.c_char * 96)]

    class sockaddr_ctl(ctypes.Structure):
        _fields_ = [
            ("sc_len", ctypes.c_uint8),
            ("sc_family", ctypes.c_uint8),
            ("ss_sysaddr", ctypes.c_uint16),
            ("sc_id", ctypes.c_uint32),
            ("sc_unit", ctypes.c_uint32),
            ("sc_reserved", ctypes.c_uint8 * 5)
        ]

    # Step 1: Create the socket
    fd = socket.socket(socket.AF_SYSTEM, socket.SOCK_DGRAM, SYSPROTO_CONTROL)
    if fd.fileno() < 0:
        raise Exception("Failed to open utun socket")

    # Step 2: Get control ID
    ci = ctl_info()
    ci.ctl_name = UTUN_CONTROL_NAME
    fcntl.ioctl(fd.fileno(), 0xC0644E03, ci)  # CTLIOCGINFO

    # Step 3: Build sockaddr_ctl
    sc = sockaddr_ctl()
    sc.sc_len = ctypes.sizeof(sockaddr_ctl)
    sc.sc_family = AF_SYS_CONTROL
    sc.ss_sysaddr = 2
    sc.sc_id = ci.ctl_id
    sc.sc_unit = 3  # gives utun2 (unit + 1)
    sc.sc_reserved = (ctypes.c_uint8 * 5)(*([0]*5))

    # Step 4: Connect socket
    addr = ctypes.string_at(ctypes.byref(sc), ctypes.sizeof(sc))
    fd.connect(addr)

    return fd.fileno()
