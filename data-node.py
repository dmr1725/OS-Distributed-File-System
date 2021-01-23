###############################################################################
#
# Filename: data-node.py
# Author: Jose R. Ortiz and ... (hopefully some students contribution)
#
# Description:
# 	data node server for the DFS
#

# Contributor: Diego Mendez

from Packet import *

import sys
import socket
import socketserver
import uuid
import os.path

def usage():
	print("""Usage: python %s <server> <port> <data path> <metadata port,default=8000>""" % sys.argv[0]) 
	sys.exit(0)


def register(meta_ip, meta_port, data_ip, data_port):
	"""Creates a connection with the metadata server and
	   register as data node
	"""
	# Establish connection
	# Fill code
	sock = socket.socket()
	sock.connect((meta_ip, meta_port))
	

 
	try:
		response = "NAK"
		sp = Packet()
		while response == "NAK":
			sp.BuildRegPacket(data_ip, data_port)
			sock.sendall(sp.getEncodedPacket())
			response = sock.recv(1024)
			response = response.decode()
			if response == "DUP":
				print("Duplicate Registration")
			
			if response == "NAK":
				print("Registratation ERROR")


	finally:
		sock.close()
	

class DataNodeTCPHandler(socketserver.BaseRequestHandler):

	def handle_put(self, p):

		"""Receives a block of data from a copy client, and 
		   saves it with an unique ID.  The ID is sent back to the
		   copy client.
		"""

		fname, fsize = p.getFileInfo()
		print(fname, 'fname del data-node.py line 62')

		data = fname.split('.')
		extension = data[1]

		self.request.send(b"OK")

		block = self.request.recv(fsize)
		try:
			block = block.decode()
		except:
			print(block) 
		
		
		print(block)

		# Generates a unique block id.
		blockid = str(uuid.uuid1())

		# Open the file for the new data block.  
		# Receive the data block.
		# Send the block id back
		# Fill code
		# naming the file as the blockid
		try:
			fd = open('storeDataBlocks/' + blockid + '.' + extension, 'w+')
			fd.write(block)
			fd.close()
		except:
			fd = open('storeDataBlocks/' + blockid + '.' + extension, 'wb')
			fd.write(block)
			fd.close()

		self.request.sendall(blockid.encode())

	def handle_get(self, p):
		
		# Get the block id from the packet
		blockid = p.getBlockID()
		print(blockid, 'line 103')


		# Read the file with the block id data
		# Send it back to the copy client.
		# Fill code
		fd = open('storeDataBlocks/' + blockid, 'rb')
		data = fd.read()
		print(data)
		fd.close()
		try:
			self.request.sendall(data.encode())
		except:
			self.request.sendall(data)

	def handle(self):
		msg = self.request.recv(1024)
		print(msg, type(msg))

		# this is to handle an error when running the function 
		if msg == b'':
			return

		p = Packet()
		p.DecodePacket(msg)

		cmd = p.getCommand()
		if cmd == "put":
			self.handle_put(p)

		elif cmd == "get":
			self.handle_get(p)
		else:
			print(msg)

if __name__ == "__main__":

	META_PORT = 8000
	if len(sys.argv) < 4:
		usage()

	try:
		HOST = sys.argv[1]
		PORT = int(sys.argv[2])
		DATA_PATH = sys.argv[3]
		if len(sys.argv) > 4:
			META_PORT = int(sys.argv[4])
		
		if not os.path.isdir(DATA_PATH):
			print("Error: Data path %s is not a directory." % DATA_PATH)
			usage()
	except:
		usage()
	


	register("localhost", META_PORT, HOST, PORT)
	server = socketserver.TCPServer((HOST, PORT), DataNodeTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
	server.serve_forever()
