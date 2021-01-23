###############################################################################
#
# Filename: meta-data.py
# Author: Jose R. Ortiz and ... (hopefully some students contribution)
#
# Description:
# 	MySQL support library for the DFS project. Database info for the 
#       metadata server.
#
# Please modify globals with appropiate info.

# Contributor: Diego Mendez


from mds_db import *
from Packet import *
import sys
import socketserver


def usage():
	print("""Usage: python %s <port, default=8000>""" % sys.argv[0]) 
	sys.exit(0)


class MetadataTCPHandler(socketserver.BaseRequestHandler):

	def handle_reg(self, db, p):
		"""Register a new client to the DFS  ACK if successfully REGISTERED
			NAK if problem, DUP if the IP and port already registered
		"""
		address = p.packet['addr']
		port = p.packet['port']
		results = db.AddDataNode(address, port)

		
		try:
			# fill code in if statement
			if results[2] != 0:
				print('yes')
				self.request.sendall(b"ACK") 
			else:
				self.request.sendall(b"DUP")
		except:
			self.request.sendall(b"NAK")

	def handle_list(self, db):
		"""Get the file list from the database and send list to client"""
		try:
			# Fill code here
			files = db.GetFiles()
			p = Packet()
			p.BuildListResponse(files)
			packet = p.getEncodedPacket() # convert to bytes
			
			self.request.sendall(packet) #sending packet back to client

		except:
			self.request.sendall("NAK")	

	def handle_put(self, db, p):
		"""Insert new file into the database and send data nodes to save
		   the file.
		"""
	    # Fill code
		# packet that comes from copy client
		info = [p.packet['fname'], p.packet['fsize']]

		
		if db.InsertFile(info[0], info[1]):
			# Fill code
			nids = db.GetDataNodes()
			print(nids, 'nids line 67 file meta-data.py')

			dataNodes_packet = Packet()
			dataNodes_packet.BuildPutResponse(nids)
			self.request.sendall(dataNodes_packet.getEncodedPacket()) # send to the copy server
			
		else:
			self.request.sendall(b"DUP") 
	
	def handle_get(self, db, p):
		"""Check if file is in database and return list of
			server nodes that contain the file.
		"""

		# Fill code to get the file name from packet and then 
		# get the fsize and array of metadata server
		fname = p.packet["fname"]
		fileInfo = db.GetFileInfo(fname)
		fsize = fileInfo[1]
		if fsize:
			# Fill code
			info = db.GetFileInode(fname)
			p.BuildGetResponse(info[1], info[0])

			self.request.sendall(p.getEncodedPacket())
		else:
			self.request.sendall("NFOUND")

	def handle_blocks(self, db, p):
		"""Add the data blocks to the file inode"""
		print(p.packet, 'handle_blocks line 98 meta-data server')

		# Fill code to get file name and blocks from
		# packet
		fname = p.packet["fname"]
		blocks = p.packet["blocks"]
	
		# Fill code to add blocks to file inode
		for address, port, chunk_id in blocks:
			result = db.AddBlockToInode(fname, [(address, port, chunk_id)])
			print(result)
			

		
	def handle(self):

		# Establish a connection with the local database
		db = mds_db("dfs.db")
		db.Connect()

		# Define a packet object to decode packet messages
		p = Packet()

		# Receive a msg from the list, data-node, or copy clients
		msg = self.request.recv(1024)
		print(msg, type(msg), 'paso 3')
		
		# Decode the packet received
		p.DecodePacket(msg)
		print(p.packet, 'paso 4')
		
	

		# Extract the command part of the received packet
		cmd = p.getCommand()

		# Invoke the proper action 
		if cmd == "reg":
			# Registration client
			self.handle_reg(db, p)

		elif cmd == "list":
			# Client asking for a list of files
			self.handle_list(db)
		
		elif cmd == "put":
			# Client asking for servers to put data
			self.handle_put(db,p)
		
		elif cmd == "get":
			# Client asking for servers to get data
			self.handle_get(db,p)

		elif cmd == "dblks":
			# Client sending data blocks for file
			self.handle_blocks(db,p)


		db.Close()

if __name__ == "__main__":
    HOST, PORT = "localhost", 8000

    if len(sys.argv) > 1:
    	try:
    		PORT = int(sys.argv[1])
    	except:
    		usage()

    server = socketserver.TCPServer((HOST, PORT), MetadataTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
