from struct import *
from Decoder import *
import socket
import threading
from Queue import Queue
from time import sleep


class Peer(threading.Thread):
# Attributes
#   ipAddress - peer ip address
#   portNumber - peer port number
#   client_id  - client_id used by application to broadcast to peers
# pm_id - id # given by PeerManager,
#               only really used for internal purposes of the pm
#   download_block_q - downloaded blocks
#               in queue to be put into the main downloaded file
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

    def __init__(self, ipAddress, portNumber,
                 info_hash, client_peer_id,
                 peer_manager):
        threading.Thread.__init__(self)
        self.peer_mgr = peer_manager
        self.ip_address = ipAddress
        self.port_number = portNumber
        self.my_socket = ''
        self.info_hash = info_hash
        self.client_peer_id = client_peer_id
        self.num_errors = 0

        # state can be
        # disconnected: all peers are init to this
        # connected: peers can connect
        # failed: peers tried to connect and failed
        #         or something went wrong and it is
        #         not doing work anymore
        # done: peer is done with work for now
        self.connection_state = 'disconnected'
        self.choking = True
        self.interested = False
        self.peer_choking = True
        self.peer_interested = False
        self.handshake_done = False
        self.write_buf = ''
        self.read_buf = ''
        self.info = (self.ip_address, self.port_number)

    def run(self):  # starts the peer thread
        while (self.connection_state == 'disconnected'):
            # Check if we exceed the errors
            if self.check_errors() is True:
                break
            self.connect()

        while (not self.peer_mgr.done_downloading() and
               self.connection_state == 'connected'):

            # Check if we exceeded the errors
            if self.check_errors() is True:
                break

            # Do a handshake if we need to
            if self.handshake_done is False:
                self.handshake()
                continue

            # Receive a message
            self.read_buf = self.my_socket.recv(100000)

            # Get the length of the message and then unpack
            msg_length = four_bytes_to_int(self.read_buf[0:4])

            # This is a keep-alive message, don't do anything
            if msg_length == 0:
                continue

            # Check to make sure we received the full message
            while msg_length > len(self.read_buf):
                try:
                    self.read_buf += self.my_socket.recv(100000)
                    print 'Recv from %s:%d success: %s' % self.info
                except socket.error as err:
                    self.num_errors += 1
                    print 'Recv from %s:%d failed: %s' % \
                        (self.ip_address, self.port_number, err)

            # It has a message id if we got this far
            msg_id = ord(self.read_buf[4])

            # Now do something depending on the message id
            handles = {
                0: self.choke_msg,
                1: self.unchoke_msg,
                2: self.interested_msg,
                3: self.uninterested_msg,
                4: self.have_msg,
                5: self.bitfield_msg,
                6: self.request_msg,
                7: self.piece_msg,
                8: self.cancel_msg,
                9: self.port_msg
                }

            # Make sure the message is a valid message
            if (msg_id > 9 and msg_id < 0):
                print 'Invalid message from %s:%d: msg_id: %d' % \
                      (self.ip_address, self.port_number, msg_id)
            else:
                handle_func = handles[msg_id]

            handle_func(self.read_buf, msg_length)

            sleep(5)

            break

        if self.connection_state == 'connected':
            self.disconnect()
        print ''

    def connect(self):
        # Try to connect, set state to fail
        # if we can't and close the connection
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.settimeout(20)
        try:
            #self.info = ('127.111.11.11', 18720)
            self.my_socket.connect(self.info)
            self.connection_state = 'connected'
            print 'Connected to %s:%d' % self.info
        except socket.error as err:
            self.num_errors += 1
            print 'Cannot connect to %s:%d: %s' % \
                  (self.info[0], self.info[1], err)

    def handshake(self):
        if self.connection_state == 'failed':
            return
        else:
            # Create the handshake message
            self.create_handshake_msg()
            self.write_buf = self.handshake_msg

            # Try to send the handshake
            # Again, if we fail, just
            # set the state to fail and
            # close the connection but
            # we can return this time
            try:
                self.my_socket.send(self.write_buf)
                print 'Sent Handshake to %s:%d' % self.info
            except socket.error as err:
                self.num_errors += 1
                print 'Send fail to %s:%d: %s' % \
                      (self.info[0], self.info[1], err)
                # self.disconnect()
                return

            # Try to receive
            # Same procedure
            try:
                self.read_buf += self.my_socket.recv(68)
                print 'Recv Handshake from: %s:%d' % self.info
                # print 'Message Length: %d' % len(self.read_buf)
                # print 'Message: ',
                # Decoder.print_hex(self.read_buf)
            except socket.error as err:
                self.num_errors += 1
                print 'Recv fail from %s:%d: %s' % \
                      (self.info[0], self.info[1], err)
                # self.disconnect()
                return

            # Now parse the handshake message
            if len(self.read_buf) > 0:
                #pstrlen = self.read_buf[0]
                msg = unpack('!8x20s20s', self.read_buf[20:68])
            else:
                self.num_errors += 1
                print 'Recv fail from %s:%d: Handshake Message Empty' % \
                      (self.info[0], self.info[1])
                # self.disconnect()
                return

            if msg[0] == self.info_hash:
                print 'Handshake from %s:%d OK' % self.info
                self.handshake_done = True
            else:
                print 'Handshake from %s:%d BAD' % self.info
                self.disconnect()
                return

    def create_handshake_msg(self):
        self.handshake_msg = '\x13BitTorrent protocol' + \
            pack('!8x20s20s',
                 self.info_hash,
                 self.client_peer_id)

    def disconnect(self):
        print 'Disconnected from %s:%d' % self.info
        self.my_socket.close()
        # later we can change this to 'disconnected'
        self.connection_state = 'failed'

    def check_errors(self):
        if self.num_errors > 3:
            print 'Peer %s:%d had more than three errors' % self.info
            self.disconnect()
            return True
        return False

    def decode_bitfield(self):
        print "decode"
        # read the bitfield from the handshaking.
        # should be able to return to the PeerMgr available blocks
        # think should use bitarray for this.
        # Makes it into an array of logicals. That would be easy
        # to index and check with

    def get_new_desired_block(self):
        return self.next_desired_block_q.get()

    def ready_to_save_blocks(self):
        # this function is called to ask the peer
        # if it has blocks in its queue ready to store into
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

    def choke_msg(self, msg, msg_len):
        print 'Choke Message from %s:%d' % self.info
        pass

    def unchoke_msg(self, msg, msg_len):
        print 'Unchoke Message from %s:%d' % self.info
        pass

    def interested_msg(self, msg, msg_len):
        print 'Interested Message from %s:%d' % self.info
        pass

    def uninterested_msg(self, msg, msg_len):
        print 'Uninterested Message from %s:%d' % self.info
        pass

    def have_msg(self, msg, msg_len):
        print 'Have Message from %s:%d' % self.info
        pass

    def bitfield_msg(self, msg, msg_len):
        print 'Bitfield Message from %s:%d' % self.info
        pass

    def request_msg(self, msg, msg_len):
        print 'Request Message from %s:%d' % self.info
        pass

    def piece_msg(self, msg, msg_len):
        print 'Piece Message from %s:%d' % self.info
        pass

    def cancel_msg(self, msg, msg_len):
        print 'Cancel Message from %s:%d' % self.info
        pass

    def port_msg(self, msg, msg_len):
        print 'Port Message from %s:%d' % self.info
        pass
