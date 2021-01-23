###############################################################################
#
# Filename: mds_db.py
# Author: Jose R. Ortiz and ... (hopefully some students contribution)
#
# Description:
# 	List client for the DFS
#

# Contributor: Diego Mendez

import socket
import sys
from Packet import *

def usage():
	print("""Usage: python %s <server>:<port, default=8000>""" % sys.argv[0])
	sys.exit(0)

def client(ip, port):
	# Contacts the metadata server and ask for list of files.
	p = Packet()
	p.BuildListPacket()
	packet = p.getEncodedPacket() # convert packet to bytes

	s = socket.socket()
	s.connect((ip, port))
	s.sendto(packet, (ip, port)) # sending packet to server

	# go to server

	packetReceived = s.recvfrom(1024) #receiving packet from server and it is a tuple
	p.DecodePacket(packetReceived[0]) # converting packet from bytes to its original type, packetReceived[0] is where the byte packet is
	packet = p.packet 
	files = packet['files']
	
	for file in files:
		print(file[0], file[1])

	

	


	

if __name__ == "__main__":

	if len(sys.argv) < 2:
		usage()

	ip = None
	port = None 
	server = sys.argv[1].split(":")
	if len(server) == 1:
		ip = server[0]
		port = 8000 
	elif len(server) == 2:
		ip = server[0]
		port = int(server[1])

	if not ip:
		usage()

	client(ip, port)
