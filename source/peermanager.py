
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
        self.data = data
        self.peer_id = data['peer_id']
        self.peers = []
        self.numwant = data['numwant']  # Start off with 50
        self.max_connections = data['max_connections']
        self.info_hash = data['info_hash']
        self.num_connected = 0
        self.TrackM = ''
        self.PieceM = ''

        self.count = 0

    def update_peer_list(self):
        # new_peers[0] is the number of peers
        # new_peers[1] is the peer list
        # look in TrackerManager to figure out what the peer list is
        new_peers = self.track_mgr.update_peer_list()

        # Parse the list
        for i in range(0, new_peers[0]):
            start = i * 12
            end = (i + 1) * 12

            # # The list is in big-endian so i'm not sure
            # # what corresponds to what. I'm just guessing.
            # peer_hex_id = new_peers[1][start:end]
            # peer_ip = "%i.%i.%i.%i" % \
            #     (int(peer_hex_id[0:2], 16),
            #      int(peer_hex_id[2:4], 16),
            #      int(peer_hex_id[4:6], 16),
            #      int(peer_hex_id[6:8], 16))
            # peer_port = int(peer_hex_id[8:12], 16)

            # self.spawn_peer(peer_ip, peer_port)

        # Only want to connect to myself now
        peer_ip = '127.000.000.001'
        peer_port = 61137

        self.spawn_peer(peer_ip, peer_port)

    def run(self):
        # enters thread
        self.manage()

    def manage(self):
        # check status of peers
        # if no peers available, call updatePeerList
        # spawn new peers that are available
        # tell peers that are choked to idle

        num = 0
        done = False
        while(not done):
            num += 1

            # Ask the Piece Manager if we are done
            pass

            # Go through and delete any failed ones
            for peer in self.peers:
                if peer.connection_state == 'failed':
                    #print 'in first loop'
                    self.num_connected -= 1
                    #print 'Peer %s:%d failed' % \
                    #      (peer.ip_address, peer.port_number)
                    self.peers.remove(peer)
                    done = True  # only here temporarily

            # Now check if we need to update the list
            if not self.peers and not done:
                #print 'in second loop'
                self.update_peer_list()

            # This will connect to peers if we need to
            if self.max_connections > self.num_connected and not done:
                #print 'in third loop'
                peers_to_add = self.max_connections - self.num_connected
                print 'Trying to connect to %d peer(s)' % peers_to_add

                for peer in self.peers:
                    if peers_to_add == 0:
                        break
                    else:
                        if peer.connection_state == 'disconnected':
                            peer.run()
                            self.num_connected += 1
                            peers_to_add -= 1
                if peers_to_add != 0:
                    self.update_peer_list()

            if num == 5:
                done = True

        self.close_peers()

    def close_peers(self):
        for peer in self.peers:
            if peer.connection_state == 'connected':
                peer.disconnect()

    def spawn_peer(self, peer_ip, peer_port):
        # Check if the peer is already in the list
        for peer in self.peers:
            if peer.ip_address == peer_ip and peer.port_number == peer_port:
                print 'multiple peer found'
                return
        peer = Peer(peer_ip, peer_port, self.data['info_hash'],
                    self.peer_id, self)
        self.peers.append(peer)

    def done_downloading(self):
        self.count += 1
        if self.count is 20:
            return True
        else:
            return False
        #return self.piece_mgr.doneDownloading()

    def print_peer_list(self):
        for peer in self.peers:
            print peer.ip_address, peer.my_state, peer.peer_state

# class Messages:
#     pass
