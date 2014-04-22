
# TODO
# currently spawning threads but not properly
# deleting the object when the thread ends
# need to clean this up and show that the manager
# has control over starting/stopping peer threads
#(4-5-14 cja)

import threading
from peers import Peer
from time import sleep
import sys

testing = True


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
        self.failed = []  # list of (ip, port, count) lists
        self.thread_locks = []
        self.numwant = data['numwant']
        self.max_connections = data['max_connections']
        self.max_no_peers = 1
        self.max_fails = 1
        self.not_enough_peers = False
        self.not_enough_peers_count = 0
        self.no_peers_online = False
        self.no_peers_online_count = 0
        self.info_hash = data['info_hash']
        self.num_running = 0
        self.track_mgr = ''
        self.piece_mgr = ''

        self.count = 0

    def update_peer_list(self):
        # new_peers[0] is the number of peers
        # new_peers[1] is the peer list
        # look in TrackerManager to figure out what the peer list is
        new_peers = self.track_mgr.update_peer_list()

        # If we get a list back that is less than the
        # number we want, set a flag
        # This should signal the manage loop not to keep asking
        # for a new peer list, only do that periodically
        if (new_peers[0] < self.max_connections):
            self.not_enough_peers = True
        else:
            self.not_enough_peers = False

        # # Only want to connect to myself
        # peer_ip = '50.155.22.20'
        # peer_port = 55223
        # if not self.peers:
        #     self.spawn_peer(peer_ip, peer_port)
        # else:
        #     if (self.peers[0].ip_address == peer_ip and
        #        self.peers[0].port_number == peer_port):
        #         pass
        #     else:
        #         self.spawn_peer(peer_ip, peer_port)

        # Prune the list
        candidate_peers = []

        for i in range(0, new_peers[0]):
            # Assume that we add it
            bool_add = True

            # Index into the hash
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

            # Check the peers list to see if it is in there
            for peer in self.peers:
                if (peer.ip_address == peer_ip and
                   peer.port_number == peer_port):
                    # Don't add it
                    bool_add = False

            for peer in self.failed:
                if (peer[0] == peer_ip and
                   peer[1] == peer_port):
                    # If it has failed more than three times
                    if peer[2] >= self.max_fails:
                        bool_add = False

            if bool_add:
                candidate_peers.append((peer_ip, peer_port))

        for peer in candidate_peers:
            self.spawn_peer(peer[0], peer[1])

        # If we can't find any peers and aren't connected to any then
        # timeout for a little while
        if not self.peers and not candidate_peers:
            self.no_peers_online = True

        if testing:
            print ''

    def run(self):
        # enters thread
        self.manage()

    def manage(self):
        # check status of peers
        # if no peers available, call updatePeerList
        # spawn new peers that are available
        # tell peers that are choked to idle

        done = False
        while(not done):

            # Ask the Piece Manager if we are done
            if self.piece_mgr.is_finished_downloading():
                done = True
                if testing:
                    print 'We are done here'
            # else:
            #     print 'We are not done here'

            # Sleep for a little bit if we can't find peers
            if self.no_peers_online:
                self.no_peers_online_count += 1
                if self.no_peers_online_count > self.max_no_peers:
                    print 'No peers'
                    exit()
                if testing:
                    print 'Can''t find any peers: Going to sleep'
                sleep(5)
                if testing:
                    print 'Looking for peers now'

            # Go through and delete any failed ones
            for peer in self.peers:
                if peer.connection_state == 'failed':
                    self.num_running -= 1

                    # See if they are in the failed list already
                    if not self.failed:
                        self.failed.append([peer.ip_address,
                                            peer.port_number, 1])
                    else:
                        # Go through all of the peers
                        for failed in self.failed:
                            # If this peer matches any failed peers
                            # Increment it's counter
                            if (peer.ip_address == failed[0] and
                               peer.port_number == failed[1]):
                                failed[2] += 1
                                if testing:
                                    print 'incremented'
                                break
                        # If we get through the whole loop and it's not there
                        # then add it to the failed list
                        self.failed.append([peer.ip_address,
                                            peer.port_number, 1])
                    # Then remove it from the list
                    self.peers.remove(peer)

            # Now check if we need to update the list
            if not self.peers and not done:
                # print 'in update loop'
                self.update_peer_list()

            # This will connect to peers if we need to
            if self.max_connections > self.num_running and not done:
                # print 'in connect loop'

                # If we don't have enough peers to connect to then connect
                # to the ones we can connect to but, only update the peer
                # list every hundreds of loops (minutes)
                if self.not_enough_peers:
                    peers_to_add = len(self.peers) - self.num_running
                else:
                    peers_to_add = self.max_connections - self.num_running

                if peers_to_add == 0:
                    pass
                else:
                    if self.not_enough_peers:
                        if testing:
                            print 'Warning: Not Enough ' + \
                                'Peers for Max Connections'

                    if testing:
                        print 'Trying to connect to %d peer(s)' % peers_to_add

                    for peer in self.peers:
                        if peers_to_add == 0:
                            break
                        else:
                            if peer.connection_state == 'init':
                                peer.start()
                                self.num_running += 1
                                peers_to_add -= 1

                                if testing:
                                    print 'Starting peer %s:%d' % peer.info

                    if peers_to_add != 0:
                        if self.not_enough_peers_count > 10000:
                            self.update_peer_list()
                            self.not_enough_peers_count = 0
                        else:
                            self.not_enough_peers_count += 1
                    if testing:
                        print ''
            if not testing:  # printing
                self.print_downloading_status()
            sleep(0.001)

        if testing:
            print 'File is done downloading'
            print 'Peer Manager Finished'

            print 'Writing out to file'
        self.piece_mgr.write_out_to_file()

        return

    def close_peers(self):
        for peer in self.peers:
            if peer.connection_state == 'done':
                print 'Disconnecting'
                peer.disconnect()

    def spawn_peer(self, peer_ip, peer_port):
        peer = Peer(peer_ip, peer_port, self.data['info_hash'],
                    self.peer_id, self.piece_mgr)
        self.peers.append(peer)
        if testing:
            print 'Spawned peer %s:%d' % (peer_ip, peer_port)

    def print_peer_list(self):
        for peer in self.peers:
            print peer.ip_address, peer.my_state, peer.peer_state

    def print_downloading_status(self):
        out = []
        out.extend('|Peers,')
        p_init = 0
        p_con = 0
        p_total = 0
        p_dis = 0
        p_fail = 0
        for peer in self.peers:
            p_total += 1
            if peer.connection_state == 'init':
                p_init += 1
            if peer.connection_state == 'connected':
                p_con += 1
            if peer.connection_state == 'disconnected':
                p_dis += 1
            if peer.connection_state == 'failed':
                p_fail += 1
        out.extend(' Con:' + str(p_con) +
                   ' Dis:' + str(p_dis) +
                   ' Fail:' + str(p_fail) +
                   ' Total:' + str(p_total) + ' |')
        piece_out = self.piece_mgr.get_print_progress()
        out.extend(piece_out)
        sys.stdout.write(''.join(out))
        sys.stdout.flush()
        # sys.stdout.flush()
        # print out
        # print out the current status. TO use during active download
        # format
        #
        #   Active Peers: num_of_peers
        #       Progress: (percent%)====================>
