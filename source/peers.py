import socket
import threading

class Peer(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		print "created a peer!"
		self.start()

	def run(self):
		print "started a new peer thread"
