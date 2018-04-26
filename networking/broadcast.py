#! /usr/bin/env python3

import sys
import socket

KNOWN_FLAGS = ["--address", "--port", "--command"]

def parse_flag(arg):
	id = arg.split("=")[0]
	v = arg.split("=")[-1]
	return [id, v] 

def udp_broadcast(argv):
	argv = argv[1:]
	size = len(argv)

	if ((size != 2)and(size != 3)):
		print("Usage:")
		print("\t./broadcast.py --address=address --port=port -command=c")
		return -1

	port=0
	address=""

	for arg in argv:
		[id, v] = parse_flag(arg)
		if not(id in KNOWN_FLAGS):
			print("flag {:s} is not known".format(id))
			return -1

		elif id == "--address":
			address = v

		elif id == "--port":
			port = int(v)

		elif id == "--command":
			command = v

	udp_tuple = (address,port)
	
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	size = sock.sendto(bytes(command, "utf-8"), udp_tuple) 
	
	while (size >= 0):
		d, addr = sock.recvfrom(16)
		size -= 1
		_buf = d.decode("utf-8")
		print('answer "{:s}" @{:s}'.format(_buf,addr[0],addr[1]))

udp_broadcast(sys.argv)
