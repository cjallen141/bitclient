from struct import *
from Decoder import *
import socket
import threading
from time import sleep
from bitstring import BitArray

testing = False

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
                 info_hash, client_peer_id, piece_mgr):
        threading.Thread.__init__(self)
        self.ip_address = ipAddress
        self.port_number = portNumber
        self.my_socket = ''
        self.info_hash = info_hash
        self.client_peer_id = client_peer_id
        self.num_errors = 0
        self.piece_mgr = piece_mgr
        self.max_errors = 5
        self.keep_alive_count = 0
        self.keep_alive_max = 50000000
        self.recv_size = 100000
        self.write_size = 100000
        self.max_timeout = 2
        self.can_receive = True
        self.cur_piece = ''
        self.block_size = 2 ** 14

        # state can be
        # init: peer manager checks this state when it tries to start
        #       new peers and will start the peer if it is in 'init'
        # connected: peers can connect
        # failed: peers tried to connect and failed
        #         or something went wrong and it is
        #         not doing work anymore
        # error: if the peer has too many errors then it errors out
        # done: peer is done with work for now
        self.connection_state = 'init'
        self.choking = True
        self.interested = False
        self.peer_choking = True
        self.peer_interested = False
        self.handshake_done = False
        self.write_buf = ''
        self.read_buf = ''
        self.info = (self.ip_address, self.port_number)

    def run(self):  # starts the peer thread
        self.connection_state = 'disconnected'

        while (self.connection_state == 'disconnected'):
            # Check if we exceed the errors
            if self.check_errors() is True:
                break
            self.connect()

        # Change it so that the peer manager tells the peer when to be done
        done = False
        while (not done):

            # Ask the Piece Manager if we are done
            if self.piece_mgr.is_finished_downloading():
                self.done()
                done = True
                continue

            # Check if we exceeded the errors
            if self.check_errors() is True:
                self.connection_state = 'failed'

            # Do a handshake if we need to
            if self.handshake_done is False:
                self.handshake()
                continue

            # Receive a message
            if self.can_receive:
                self.read_buf = self.my_socket.recv(self.recv_size)

                # Get the length of the message and then unpack
                msg_length = four_bytes_to_int(self.read_buf[0:4])

                # This is a keep-alive message, don't do anything
                if msg_length == 0:
                    continue

                # Check to make sure we received the full message
                while msg_length > len(self.read_buf):
                    try:
                        self.read_buf += self.my_socket.recv(self.recv_size)
                        if testing: print 'Recv from %s:%d success' % self.info
                    except socket.error as err:
                        self.num_errors += 1
                        if testing: print 'Recv from %s:%d failed: %s' % \
                            (self.ip_address, self.port_number, err)

                # There might be multiple messages in the buffer
                # Loop through them
                while (len(self.read_buf) > 0):
                    msg_length = four_bytes_to_int(self.read_buf[0:4])

                    if msg_length == 0:
                        continue

                    # It has a message id if we got this far
                    msg_id = ord(self.read_buf[4])
                    msg_header = self.read_buf[0:5]
                    msg_payload = self.read_buf[5:msg_length + 5 - 1]

                    # pack it into a data structure
                    pack_str = '!ib5s%ds' % (msg_length - 1)
                    message = pack(pack_str, msg_length, msg_id,
                                   msg_header, msg_payload)

                    # Run the handler
                    handles = {
                        0: self.recv_choke_msg,
                        1: self.recv_unchoke_msg,
                        2: self.recv_interested_msg,
                        3: self.recv_uninterested_msg,
                        4: self.recv_have_msg,
                        5: self.recv_bitfield_msg,
                        6: self.recv_request_msg,
                        7: self.recv_piece_msg,
                        8: self.recv_cancel_msg,
                        9: self.recv_port_msg
                    }

                    # Now do something depending on the message id
                    # Make sure the message is a valid message
                    if (msg_id > 9 and msg_id < 0):
                        self.num_errors += 1
                        if testing: print 'Invalid message from %s:%d: msg_id: %d' % \
                              (self.ip_address, self.port_number, msg_id)
                    else:
                        handle_func = handles[msg_id]

                    handle_func(message, pack_str)

                    self.read_buf = self.read_buf[4 + msg_length:]

            # Are we choked, if not send a request
            if self.peer_choking is False:
                # Get a piece to request if we don't have one
                if self.cur_piece == '':
                    self.get_new_desired_piece()
                    if self.cur_piece == '':
                        self.done()
                else:
                    # Get a block to request
                    self.cur_block = self.get_new_desired_block()
                    if self.cur_block == '':
                        # All the blocks have been downloaded
                        self.cur_piece.is_downloaded()
                        self.piece_mgr.downloaded_piece_q.put(self.cur_piece)
                        if testing: print 'Downloaded Piece %d from %s:%d' % \
                              (self.cur_piece.idx, self.info[0], self.info[1])
                        self.cur_piece = ''
                    else:
                        # Call the request function
                        self.send_request_msg(self.cur_block)

            # Send a message
            # This can hold multiple messages, because each send
            # function just adds to the write_buffer.
            try:
                self.can_receive = False
                if self.write_buf:
                    self.my_socket.sendall(self.write_buf)
                    if testing: print 'Sent message to %s:%d' % self.info
                    self.write_buf = ''

                    # Sent something so receive the message
                    self.can_receive = True
                else:
                    # Keep the connection alive
                    self.keep_alive_count += 1
                    if self.check_keep_alive():
                        # Create the keep alive message
                        self.my_socket.sendall('')
                        if testing: print 'Sent keep alive to %s:%d' % self.info
            except socket.error as err:
                self.can_receive = False
                self.num_errors += 1
                if testing: print 'Cannot send to %s:%d: %s' % \
                    (self.info[0], self.info[1], err)

            if testing: print ''

        return

    def connect(self):
        # Try to connect, set state to fail
        # if we can't and close the connection
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.settimeout(self.max_timeout)
        try:
            #self.info = ('127.111.11.11', 18720)
            self.my_socket.connect(self.info)
            self.connection_state = 'connected'
            if testing: print 'Connected to %s:%d' % self.info
        except socket.error as err:
            self.num_errors += 1
            if testing: print 'Cannot connect to %s:%d: %s' % \
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
                self.write_buf = ''
                if testing: print 'Sent Handshake to %s:%d' % self.info
            except socket.error as err:
                self.num_errors += 1
                if testing: print 'Send fail to %s:%d: %s' % \
                      (self.info[0], self.info[1], err)
                # self.disconnect()
                return

            # Try to receive
            # Same procedure
            try:
                self.read_buf += self.my_socket.recv(68)
                if testing: print 'Recv Handshake from: %s:%d' % self.info
                # print 'Message Length: %d' % len(self.read_buf)
                # print 'Message: ',
                # Decoder.print_hex(self.read_buf)
            except socket.error as err:
                self.num_errors += 1
                if testing: print 'Recv fail from %s:%d: %s' % \
                      (self.info[0], self.info[1], err)
                # self.disconnect()
                return

            # Now parse the handshake message
            if len(self.read_buf) > 0:
                #pstrlen = self.read_buf[0]
                msg = unpack('!8x20s20s', self.read_buf[20:68])
            else:
                self.num_errors += 1
                if testing: print 'Recv fail from %s:%d: Handshake Message Empty' % \
                      (self.info[0], self.info[1])
                # self.disconnect()
                return

            if msg[0] == self.info_hash:
                if testing: print 'Handshake from %s:%d OK' % self.info
                self.handshake_done = True
            else:
                if testing: print 'Handshake from %s:%d BAD' % self.info
                self.disconnect()
                return

    def create_handshake_msg(self):
        self.handshake_msg = '\x13BitTorrent protocol' + \
            pack('!8x20s20s',
                 self.info_hash,
                 self.client_peer_id)

    # A peer has disconnected for some reason
    # Basically the same as failed now
    def disconnect(self):
        if testing: print 'Peer %s:%d disconnected' % self.info
        self.my_socket.close()
        # later we can change this to 'disconnected'
        self.connection_state = 'disconnected'
        self.reset_vars()
        return

    # A peer failed if they have more than the max number of errors
    # Kill the thread
    def failed(self):
        if testing: print 'Peer %s:%d failed' % self.info
        self.my_socket.close()
        self.connection_state = 'failed'
        self.reset_vars()
        return

    # A peer has done all the work it can find. 
    def done(self):
        if testing: print 'Peer %s:%d done' % self.info
        self.my_socket.close()
        self.connection_state = 'done'
        self.reset_vars()
        return

    def reset_vars(self):
        self.num_errors = 0
        self.choking = True
        self.interested = False
        self.peer_choking = True
        self.peer_interested = False
        self.handshake_done = False
        self.read_buf = ''
        self.write_buf = ''

    def check_errors(self):
        if self.num_errors > self.max_errors:
            if testing: print 'Peer %s:%d exceeded max errors' % self.info
            self.failed()
            return True
        return False

    def check_keep_alive(self):
        if self.keep_alive_count > self.keep_alive_max:
            self.keep_alive_count = 0
            return True

    def get_new_desired_piece(self):
        done = False
        while (not done):
            # Get a piece
            candidate_piece = self.piece_mgr.desired_piece_q.get()

            # Check the piece to see if the peer has it
            if not self.bit_field[candidate_piece.idx]:
                # Put it back into the queue
                self.piece_mgr.desired_piece_q.put(candidate_piece)
            else:
                self.cur_piece = candidate_piece
                done = True

    def get_new_desired_block(self):
        # Go through each block and find one that we don't have
        for block in self.cur_piece.blocks:
            if not block.downloaded:
                return block
        # If we get here then there are no blocks to download
        return ''

    # def ready_to_save_blocks(self):
    # this function is called to ask the peer
    # if it has blocks in its queue ready to store into
    # the main block storage.
    #     return not self.download_block_q.empty()

    # def add_block_to_queue(self, block):
    #     self.download_block_q.put(block)

    # def get_downloaded_blocks(self):
    # returns all the objects currently in the download block queue
    # returned as list in no particular order
    #     x = []
    #     while not self.download_block_q.empty():
    #         x.append(self.download_block_q.get())

    #     if self.download_block_q.empty():
    #         print 'emptied peer queue'
    #     return x

#
# Receiving Messages
#

    # The peer is choking you
    def recv_choke_msg(self, data, pack_str):
        if testing: print 'Choke Message from %s:%d' % self.info
        self.peer_choking = True

    # The peer is unchoking you, can now make requests
    def recv_unchoke_msg(self, msg, msg_len):
        if testing: print 'Unchoke Message from %s:%d' % self.info
        self.peer_choking = False

    # The peer is interested in getting something from you
    def recv_interested_msg(self, msg, msg_len):
        if testing: print 'Interested Message from %s:%d' % self.info

    # The peer is not interested in getting anything from you
    def recv_uninterested_msg(self, msg, msg_len):
        if testing: print 'Uninterested Message from %s:%d' % self.info

    def recv_have_msg(self, data, pack_str):
        if testing: print 'Have Message from %s:%d' % self.info

        # Unpack the structure
        msg = unpack(pack_str, data)
        # print 'length: %d\nid: %d' % (msg[0], msg[1])
        # print 'header(%d): ' % len(msg[2]),
        # print_escaped_hex(msg[2], True)
        # print 'message(%d): ' % len(msg[3]),
        # print_escaped_hex(msg[3], True)

        # Update the bit array
        self.bit_field[four_bytes_to_int(msg[3])] = True

        # Call bit_field_analyze
        self.bitfield_analyze()

    def recv_bitfield_msg(self, data, pack_str):
        if testing: print 'Bitfield Message from %s:%d' % self.info

        # Unpack the structure
        msg = unpack(pack_str, data)
        # print 'length: %d\nid: %d' % (msg[0], msg[1])
        # print 'header(%d): ' % len(msg[2]),
        # print_escaped_hex(msg[2], True)
        # print 'message(%d): ' % len(msg[3]),
        # print_escaped_hex(msg[3], True)

        # Put into bitarray
        self.bit_field = BitArray(bytes=msg[3])

        # Call bit_field_analyze
        self.bitfield_analyze()

    def recv_request_msg(self, msg, msg_len):
        if testing: print 'Request Message from %s:%d' % self.info

    def recv_piece_msg(self, data, pack_str):
        if testing: print 'Piece Message from %s:%d' % self.info

        # Unpack the structure
        msg = unpack(pack_str, data)
        # Take out the piece offset and block offset
        pack_str = '!2i%ds' % (len(msg[3])-8)
        payload = unpack(pack_str, msg[3])
        if testing:
            print 'length: %d' % msg[0]
            print 'id: %d' % msg[1]
            print 'header(%d): ' % len(msg[2]),
            print_escaped_hex(msg[2], True)
            print 'piece offset(4): %d' % payload[0]
            print 'block offset(4): %d' % payload[1]
        # print 'message(%d): ' % len(payload[2]),
        # print_escaped_hex(payload[2], True)

        self.cur_block.data = payload[2]
        self.cur_block.downloaded = True
        self.cur_block = ''

    def recv_cancel_msg(self, msg, msg_len):
        if testing: print 'Cancel Message from %s:%d' % self.info

    def recv_port_msg(self, msg, msg_len):
        if testing: print 'Port Message from %s:%d' % self.info

#
# Sending Messages
#

    def send_choke_msg(self, msg, msg_len):
        if testing: print 'Choke Message to %s:%d' % self.info

    def send_unchoke_msg(self, msg, msg_len):
        if testing: print 'Unchoke Message to %s:%d' % self.info

    def send_interested_msg(self):
        if testing: print 'Interested Message to %s:%d' % self.info
        msg = pack('!ib', 1, 2)

        self.write_buf = self.write_buf + msg

    def send_unintersted_msg(self, msg, msg_len):
        if testing: print 'Unintersted Message to %s:%d' % self.info

    def send_have_msg(self, msg, msg_len):
        if testing: print 'Have Message to %s:%d' % self.info

    def send_bitfield_msg(self, msg, msg_len):
        if testing: print 'Bitfield Message to %s:%d' % self.info

    def send_request_msg(self, block):
        if testing: print 'Request Message to %s:%d' % self.info
        # Create the packet
        pack_str = '!ibiii'
        msg = pack(pack_str, 13, 6, self.cur_piece.idx,
                   block.offset_idx, block.block_size)
        self.write_buf = self.write_buf + msg

    def send_piece_msg(self, msg, msg_len):
        if testing: print 'Piece Message to %s:%d' % self.info

    def send_cancel_msg(self, msg, msg_len):
        if testing: print 'Cancel Message to %s:%d' % self.info

    def send_port_msg(self, msg, msg_len):
        if testing: print 'Port Message to %s:%d' % self.info

#
# Below are all the function that the messages use
#

    # Checks whether we need to send an intersted message
    def bitfield_analyze(self):
        if self.interested is False:
            # Ask the piece manager whether we need to be intersted
            self.interested = self.piece_mgr.is_interested(self.bit_field)
            if self.interested is True:
                self.send_interested_msg()
