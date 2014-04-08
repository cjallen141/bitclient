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
# q
# availablePieces
# requestedBlock
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# handshake()
# decode_bitfield()
# request_block()
# check_requested_block()
# return_block()
# send_block_request()
# request_block_from_peer()
# dump_blocks_to_peer_manager()
# listen_for_incoming_requests()

	def __init__(self,pm_id, client_id, ipAddress, portNumber ):
		threading.Thread.__init__(self)
		self.client_id = client_id
		self.ipAddress = ipAddress
		self.portNumber= portNumber

		self.block_q = Queue(0)
		
	def run(self): #starts the peer thread
		
		
		self.connect()
		
		print 'Thread:' + str(self.client_id) + 'done!'

	def connect(self):
		print 'Address:' + self.ipAddress + '\nport: ' + str(self.portNumber)










	def test_peer(self):
		self.x = 0 
		while self.x<1000000:
			self.x=self.x+1
		

#########TESTING CODE############

peer = Peer(0, 2020,'192.168.1.1',3251)

print peer.ipAddress
peer.run()
