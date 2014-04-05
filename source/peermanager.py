import socket
import math

from bitstring import BitArray
from tracker import TrackerManager

class PeerManager(object):
	# attributes:
	#		peers[] - list of all managed peers
	#		peerID  - self ID for connecting to peers
	
	#methods
	#
	#	manage() 
	#		-- main loop that does the work
	# 	check_status_of_peers() 
	#		-- 
	#	update_peer_list()
	#		-- 	call to get an updated peer list from the TrackerMgr
	#	spawn_peer()
	#		-- create a new peer, this also spawns a thread for the peer
	#	kill_peer()
	#		--cleans up the peer and deletes the thread


	def __init__(self, peerID, tracker_mgr):

		self.peerID = peerID
		self.peers = []
		self.tracker_mgr = tracker_mgr


##################TESTING CODE

#create a tracker object
tracker = TrackerManager()
#create peermanager object
peer_mgr = PeerManager(2230, tracker)
print peer_mgr.peerID