###############################################################################
#
# Filename: mds_db.py
# Author: Jose R. Ortiz and ... (hopefully some students contribution)
#
# Description:
# 	Copy client for the DFS
#
#

# Contributor: Diego Mendez

import socket
import sys
import os.path
from mds_db import *

from Packet import *

def isPortRunning(host, port):
	#This function checks if port is running to send data to it. You don't want to send to a server that it is not running
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


def usage():
	print("""Usage:\n\tFrom DFS: python %s <server>:<port>:<dfs file path> <destination file>\n\tTo   DFS: python %s <source file> <server>:<port>:<dfs file path>""" % (sys.argv[0], sys.argv[0]))
	sys.exit(0)

def copyToDFS(address, fname, path):
	""" Contact the metadata server to ask to copy file fname,
	    get a list of data nodes. Open the file in path to read,
	    divide in blocks and send to the data nodes. 
	"""
	print('hola')
	
	# Create a connection to the data server
	# Fill code
	sock = socket.socket()
	sock.connect(address)

	# Read file
	# Fill code
	fd = open('./' + path, "rb") #  path is the name of the file stored in our local directory
	block_list = [] # block list of the file
	contents = fd.read() # content from the file
	fd.close()

	# Create a Put packet with the fname and the length of the data,
	# and sends it to the metadata server 
	# Fill code
	p = Packet() 
	size = os.path.getsize('./' + path)
	p.BuildPutPacket(fname, size)
	file_attributes = p.packet # contains the dictionary {"command": "put", "fname": fname, "size": size} from the property self.packet
	sock.sendall(p.getEncodedPacket()) # send to meta data server the put packet; self.packet = {"command": "put", "fname": fname, "size": size}
	

	# If no error or file exists
	# Get the list of data nodes.
	# Divide the file in blocks
	# Send the blocks to the data servers

	# Fill code
	response = sock.recv(1024) # data nodes from meta-data to save the file
	sock.close()
	sock = None
	if response != b'DUP':
		p.DecodePacket(response)
	else:
		print('DUP')
		return
	data_nodes = p.packet
	data_nodes = data_nodes["servers"]
	parts = int(len(contents) / len(data_nodes)) # each block list will contain this size "parts"
	print(data_nodes, 'response of data nodes')
	print(file_attributes, 'file_attributes')

	newDataNodes = [] # will contain the data nodes that are running
	for host, port in data_nodes:
		isRunning = isPortRunning(host, port)
		if isRunning:
			print(host, port, 'RUNNING')
			newDataNodes.append([host,port])
	
	data_nodes = newDataNodes
	print(data_nodes, 'data nodes running')

	# dividing the file over the number of data servers
	fd = open('./' + path, "rb")
	newContents = fd.read(parts)
	contents_left = len(contents) % parts # the characters left
	for i in range(len(data_nodes)):
		if i == len(data_nodes)-2:
			block_list.append(newContents)
			newContents = fd.read(parts + contents_left)
		else:
			block_list.append(newContents)
			newContents = fd.read(parts)
	print(block_list, 'blocks of data')
	fd.close()


	# sending the blocks to the data servers
	data = []
	for i in range(len(data_nodes)):
		host = data_nodes[i][0]
		port = data_nodes[i][1]
		block = block_list[i]

		sock = socket.socket()
		sock.connect((host,port))
		p.BuildPutPacket(path, size)
		# p.BuildPutResponse(block_list[i]) # block of data, i is the number of the new file
		sock.sendall(p.getEncodedPacket())
		response = sock.recv(1024)
		print(response, 'line 155')
		print(type(block_list[i]), 'line 116')
		try:
			sock.sendall(block_list[i].encode())
		except:
			sock.sendall(block_list[i])

		# if type(block_list[i]) == 'bytes':
		# 	sock.sendall(block_list[i])
		# else:
		# 	sock.sendall(block_list[i].encode())
		chunk_id = sock.recv(1024)
		chunk_id = chunk_id.decode() # chunk_id or uuid
		data.append((host,port,chunk_id))
		sock.close()
		sock = None

	sock = socket.socket()
	sock.connect(address) # connect socket to meta data server to send new block packet

	# Notify the metadata server where the blocks are saved.
	# Fill code
	p.BuildDataBlockPacket(fname, data)
	sock.sendall(p.getEncodedPacket())

	sock.close()
	sock = None

	
	
def copyFromDFS(address, fname, path):
	""" Contact the metadata server to ask for the file blocks of
	    the file fname.  Get the data blocks from the data nodes.
	    Saves the data in path.
	"""
	data = fname.split('.')
	file_extension = data[1]
   	# Contact the metadata server to ask for information of fname
	sock = socket.socket()
	sock.connect(address)

	p = Packet()
	p.BuildGetPacket(fname)
	sock.sendall(p.getEncodedPacket())


	# Fill code

	# If there is no error response Retreive the data blocks
	response = sock.recv(1024) # from meta data server
	sock.close()
	sock = None
	p.DecodePacket(response)
	blocks = p.packet["servers"]
	chunks_toSave = [] # chunks that are going to be saved in file 'path'
	for host, port, chunk_id in blocks:
		print(host, port, chunk_id)
		sock = socket.socket()
		sock.connect((host,port))
		p.BuildGetDataBlockPacket(chunk_id + '.' + file_extension)
		sock.sendall(p.getEncodedPacket())
		data_block = sock.recv(1024)
		try:
			data_block = data_block.decode()
		except:
			print(data_block)
		chunks_toSave.append(data_block)
		print(data_block, 'me le devuelve el data node')
		sock.close()
		sock = None
	
	try:
		fd = open(path, "w")
		for chunk in chunks_toSave:
			fd.write(chunk)
		fd.close()
	except:
		fd = open(path, "wb")
		for chunk in chunks_toSave:
			fd.write(chunk)
		fd.close()



if __name__ == "__main__":
#	client("localhost", 8000)
	if len(sys.argv) < 3:
		usage()

	file_from = sys.argv[1].split(":")
	file_to = sys.argv[2].split(":")
	print(file_to)
	if len(file_from) > 1:
		print('hola')
		ip = file_from[0]
		port = int(file_from[1])
		from_path = file_from[2]
		to_path = sys.argv[2]

		if os.path.isdir(to_path):
			print("Error: path %s is a directory.  Please name the file." % to_path)
			usage()
		print(from_path, to_path)
		copyFromDFS((ip, port), from_path, to_path)

	elif len(file_to) > 2:
		print('dimelo')
		ip = file_to[0]
		port = int(file_to[1])
		to_path = file_to[2]
		from_path = sys.argv[1]

		if os.path.isdir(from_path):
			print("Error: path %s is a directory.  Please name the file." % from_path)
			usage()
		copyToDFS((ip, port), to_path, from_path)


