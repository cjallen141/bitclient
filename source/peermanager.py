
# TODO
# currently spawning threads but not properly
# deleting the object when the thread ends
# need to clean this up and show that the manager
# has control over starting/stopping peer threads
#(4-5-14 cja)

import threading
from peers import Peer
import socket


class PeerManager(threading.Thread):
    # attributes:
    #       peers[] - list of all connected peers
    #       candidate_peers[] - list of unconnected peers
    #       peerID  - self ID for connecting to peers

    # methods
    #
    #   manage()
    #       -- main loop that does the work
    #   check_status_of_peers()
    #       --
    #   update_peer_list()
    #       --  call to get an updated peer list from the TrackerMgr
    #   spawn_peer()
    #       -- create a new peer, this also spawns a thread for the peer
    #   kill_peer()
    #       --cleans up the peer and deletes the thread
    #   run()
    #       -this is where the thread enters

    def __init__(self, data):
        threading.Thread.__init__(self)
        self.peerID = data['peer_id']
        self.peers = []
        self.numwant = 50  # Start off with 50
        self.max_connections = data['max_connections']
        self.num_connected = 0
        self.TrackM1 = ''
        self.PieceM1 = ''

    def update_peer_list(self):
        # new_peers[0] is the number of peers
        # new_peers[1] is the peer list
        # look in TrackerManager to figure out what the peer list is
        new_peers = self.TrackM.update_peer_list()

        # Parse the list
        for i in range(0, new_peers[0]):
            start = i * 12
            end = (i + 1) * 12

            # The list is in big-endian so i'm not sure
            # what corresponds to what. I'm just guessing.
            peer_hex_id = new_peers[1][start:end]
            peer_ip = "%i.%i.%i.%i" % \
                (int(peer_hex_id[0:2], 16),
                 int(peer_hex_id[2:4], 16),
                 int(peer_hex_id[4:6], 16),
                 int(peer_hex_id[6:8], 16))
            peer_port = int(peer_hex_id[8:12], 16)

            mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #mySocket.setblocking(0)

            self.spawn_peer(peer_ip, peer_port, mySocket)

    # Connect to one peer for now
    def connect_to_peers(self):
        if self.max_connections > self.num_connected:
            # How many should we add
            peers_to_add = self.max_connections - self.num_connected
            print 'Trying to connect to %d more peer(s)' % (peers_to_add)

            # Find a peer to connect to
            for peer in self.peers:
                if peers_to_add == 0:
                    break
                else:
                    if peer.connection_state is False:
                        try:
                            peer.my_socket.connect((peer.ip_address,
                                                    peer.port_number))
                            peer.connection_state = True
                            print 'connected to %s:%d' % \
                                  (peer.ip_address, peer.port_number)
                            peers_to_add -= 1
                        except socket.error, e:
                            print 'Error: %s' % e

    def run(self):
        # enters thread
        self.manage()

    def manage(self):
        # check status of peers
        # if no peers available, call updatePeerList
        # spawn new peers that are available
        # tell peers that are choked to idle

        # First get a list of peers from the tracker
        self.update_peer_list()

        # Then connect to some peers
        self.connect_to_peers()

        self.close_peers()

    def close_peers(self):
        for peer in self.peers:
            if peer.connection_state is True:
                peer.my_socket.close()
                peer.connection_state = False
                print 'disconnected from %s:%d' % \
                      (peer.ip_address, peer.port_number)

    def spawn_peer(self, peer_ip, peer_port, mySocket):
        peer = Peer(peer_ip, peer_port, mySocket)
        self.peers.append(peer)

    def print_peer_list(self):
        for peer in self.peers:
            print peer.ip_address, peer.my_state, peer.peer_state

# class Messages:
#     pass
