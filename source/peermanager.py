
########TODO
# currently spawning threads but not properly deleting the object when the thread ends
# need to clean this up and show that the manager has control over starting/stopping peer threads
#(4-5-14 cja)


from tracker import TrackerManager
import threading
from peers import Peer

class PeerManager(threading.Thread):
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
	#	run()
	#		-this is where the thread enters


	def __init__(self, peerID, tracker_mgr):
		threading.Thread.__init__(self)
		self.peerID = peerID
		self.peers = []
		self.tracker_mgr = tracker_mgr

	def update_peer_list(self):
		new_peers = self.tracker_mgr.update_peer_list()

		#only adds if not already in peers list
		for np in new_peers:
			if np not in self.peers:
				##self.peers.append(np)  this is the original, removed for testing (cja)
				self.peers.append(Peer(np))
		print "finished adding peers"
		
	def run(self):
		#enters thread
		print "starting Peer Manager..."
		self.manage()
		print "closing Peer Manager..."


	def manage(self):
		#check status of peers
		####if no peers available, call updatePeerList
		####spawn new peers that are available
		####tell peers that are choked to idle
		x = 0
		while x<2:
			#checking if there are any peers
			if len(self.peers) == 0:
				self.update_peer_list()


				for peer in self.peers:
					peer.start()
				
				x=x+1
				print x
			self.peers[:] = [peer for peer in self.peers if peer.isAlive()]
			

				
	
	def spawn_peer(self):
		peer = Peer(self.peerID)
		self.peers.append(Peer())


##################TESTING CODE##################

# #create a tracker object
# tracker = TrackerManager()
# #create peermanager object
# peer_mgr = PeerManager(2230, tracker)


# peer_mgr.start()#starts the thread

