import socket
import threading

class Peer(threading.Thread):

	def __init__(self,id):
		threading.Thread.__init__(self)
		self.id = id


		self.start()
		
	def run(self):
		print "started a new peer thread"
		self.x = 0 

		while self.x<1000000:
			self.x=self.x+1
		print 'Thread:' + self.id + 'done!'

