import socket
import threading
from Queue import Queue


class Peer(threading.Thread):
# Attributes
# 	ipAddress - peer ip address
# 	portNumber - peer port number
#	client_id  - client_id used by application to broadcast to peers
# pm_id	- id # given by PeerManager,
#				only really used for internal purposes of the pm
#	download_block_q - downloaded blocks
#				in queue to be put into the main downloaded file
# activeFlag
# availablePieces - Dictionary of available pieces
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

    def __init__(self, ipAddress, portNumber, mySocket):
        threading.Thread.__init__(self)
        self.ipAddress = ipAddress
        self.portNumber = portNumber
        self.mySocket = mySocket

        # set internals
        self.connection_alive = 0

    def run(self):  # starts the peer thread

        self.connect()

        print 'Thread:' + str(self.client_id) + 'done!'

    def is_connection_alive(self):
        return connection_alive

    def connect(self):
        print 'Address:' + self.ipAddress + '\nport: ' + str(self.portNumber)

        # handle the socket connection

    def decode_bitfield(self):
        print "decode"
        # read the bitfield from the handshaking.
        # should be able to return to the PeerMgr available blocks
        # think should use bitarray for this. Makes it into an array of logicals. That would be easy
        # to index and check with

    def get_new_desired_block(self):
        return self.next_desired_block_q.get()

    def ready_to_save_blocks(self):
        # this function is called to ask the peer if it has blocks in its queue ready to store into
        # the main block storage.
        return not self.download_block_q.empty()

    def add_block_to_queue(self, block):
        self.download_block_q.put(block)

    def get_downloaded_blocks(self):
        # returns all the objects currently in the download block queue
        # returned as list in no particular order
        x = []
        while not self.download_block_q.empty():
            x.append(self.download_block_q.get())

        if self.download_block_q.empty():
            print 'emptied peer queue'
        return x




# TESTING CODE############

# testing next_desired_block_q

# blocks_q = Queue(0)
# blocks_q.put('0')
# blocks_q.put('1')
# blocks_q.put('2')
# blocks_q.put('3')

# peer = Peer(0, 2020,'192.168.1.1',3251,blocks_q)

# peer.

# print peer.ipAddress
# peer.run()

# print "\n\n\######checking queueing of peer queue"
# print "peer ready to save blocks:"
# print peer.ready_to_save_blocks()
# print "\n Adding blocks"
# peer.add_block_to_queue('1')
# peer.add_block_to_queue('2')
# peer.add_block_to_queue('3')
# print "peer ready to save blocks:"
# print peer.ready_to_save_blocks()

# x = peer.get_downloaded_blocks()
# print x

# print peer.ready_to_save_blocks()
# print "\n Adding blocks"
# peer.add_block_to_queue('1123123')
# peer.add_block_to_queue('12312312312312')
# peer.add_block_to_queue('32')
# print "peer ready to save blocks:"
# print peer.ready_to_save_blocks()

# x = peer.get_downloaded_blocks()
# print x
