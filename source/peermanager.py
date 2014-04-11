
# TODO
# currently spawning threads but not properly
# deleting the object when the thread ends
# need to clean this up and show that the manager
# has control over starting/stopping peer threads
#(4-5-14 cja)

import threading
from peers import Peer


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

    def __init__(self, peerID):
        threading.Thread.__init__(self)
        self.peerID = peerID
        self.peers = []
        self.candidate_peers = []
        self.numwant = 50  # Start off with 50 and go down
        self.TrackM1 = ''
        self.PieceM1 = ''

    def update_peer_list(self):
        # new_peers[0] is the number of peers
        # new_peers[1] is the peer list
        # look in TrackerManager to figure out what the peer list is
        new_peers = self.TrackM1.update_peer_list()
        peer_id = []

        # Parse the list
        for i in range(0, new_peers[0]):
            start = i * 12
            end = (i + 1) * 12

            # The list is in big-endian so i'm not sure
            # what corresponds to what. I'm just guessing.
            peer_hex_id = new_peers[1][start:end]
            peer_ip = peer_hex_id[0:8]
            peer_port = peer_hex_id[8:13]
            one_peer = [str(int(peer_ip[0:2], 16)) +
                        '.' + str(int(peer_ip[2:4], 16)) +
                        '.' + str(int(peer_ip[4:6], 16)) +
                        '.' + str(int(peer_ip[6:8], 16)) +
                        ':' + str(int(peer_port, 16))]

            peer_id.append(one_peer)
            # print '%02i' % i,
            # print '%03i' % start,
            # print '%03i' % end,
            # print peer_hex_id,
            # print peer_ip,
            # print peer_port

        # Wrap it up into a [peer_ip, peer_port]
        self.candidate_peers = peer_id

    def run(self):
        # enters thread
        print "starting Peer Manager..."
        self.manage()
        print "closing Peer Manager..."

    def manage(self):
        # check status of peers
        # if no peers available, call updatePeerList
        # spawn new peers that are available
        # tell peers that are choked to idle
        x = 0
        while x < 2:
            # checking if there are any peers
            if len(self.peers) == 0:
                self.update_peer_list()

                for peer in self.peers:
                    peer.start()

                x = x + 1
                print x
            self.peers[:] = [peer for peer in self.peers if peer.isAlive()]

    def spawn_peer(self):
        peer = Peer(self.peerID)
        self.peers.append(Peer())


# TESTING CODE##################

# create a tracker object
# tracker = TrackerManager()
# create peermanager object
# peer_mgr = PeerManager(2230, tracker)


# peer_mgr.start()#starts the thread
