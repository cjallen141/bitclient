import socket
import threading
from Queue import Queue
class Peer(threading.Thread):
#Attributes
# 	ipAddress - peer ip address
# 	portNumber - peer port number
#	client_id  - client_id used by application to broadcast to peers
#	pm_id	- id # given by PeerManager, only really used for internal purposes of the pm
#	block_q - downloaded blocks in queue to be put into the main downloaded file
# activeFlag
# availablePieces
# requestedBlock
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# handshake()
# decode_bitfield()
# request_block()
# check_requested_block()
# is_connection_alive()
# return_block()
# send_block_request()
# request_block_from_peer()
# ready_to_save_blocks()
# get_downloaded_blocks()
# listen_for_incoming_requests()

	def __init__(self,pm_id, client_id, ipAddress, portNumber ):
		threading.Thread.__init__(self)
		self.client_id = client_id
		self.ipAddress = ipAddress
		self.portNumber= portNumber

		self.block_q = Queue(0)
		

		#set internals
		self.connection_alive = 0
	def run(self): #starts the peer thread
		
		
		self.connect()
		
		print 'Thread:' + str(self.client_id) + 'done!'

	def connect(self):
		print 'Address:' + self.ipAddress + '\nport: ' + str(self.portNumber)

		#handle the socket connection 


	def is_connection_alive(self):
		return connection_alive



	def ready_to_save_blocks(self):
		#this function is called to ask the peer if it has blocks in its queue ready to store into 
		# the main block storage. 
		return not self.block_q.empty()

	def add_block_to_queue(self, block):
		self.block_q.put(block)


	def get_downloaded_blocks(self):
		#returns all the objects currently in the download block queue
		#returned as list in no particular order
		x = []
		while not self.block_q.empty():
			x.append(self.block_q.get())

		if self.block_q.empty():
			print 'emptied peer queue'
		return x




#########TESTING CODE############

peer = Peer(0, 2020,'192.168.1.1',3251)

print peer.ipAddress
peer.run()

print "\n\n\######checking queueing of peer queue"
print "peer ready to save blocks:"
print peer.ready_to_save_blocks()
print "\n Adding blocks"
peer.add_block_to_queue('1')
peer.add_block_to_queue('2')
peer.add_block_to_queue('3')
print "peer ready to save blocks:"
print peer.ready_to_save_blocks()

x = peer.get_downloaded_blocks()
print x

print peer.ready_to_save_blocks()
print "\n Adding blocks"
peer.add_block_to_queue('1123123')
peer.add_block_to_queue('12312312312312')
peer.add_block_to_queue('32')
print "peer ready to save blocks:"
print peer.ready_to_save_blocks()

x = peer.get_downloaded_blocks()
print x
