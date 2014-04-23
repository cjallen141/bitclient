# Tracker Manager Class
from Decoder import *
import requests
import socket
import struct
import random
import urlparse

testing = True


class TrackerManager:
    # Attributes

    # Constructors
    def __init__(self, data):
        self.data = data
        self.announce_url = data['announce']

        self.peer_mgr = ''
        self.piece_mgr = ''
        self.cur_url = ''

    # Methods
    def connect_to_tracker(self, info_hash, peer_id, length,
                           state, port, compact, no_peer_id,
                           key, downloaded, uploaded, corrupt,
                           numwant):

        # Try udp trackers first
        for url in self.announce_url:
            print 'Trying to contact ' + url
            if 'udp://' in url:
                parsed_url = urlparse.urlparse(url)
                print parsed_url.hostname
                print parsed_url.port
                ip_address = socket.gethostbyname(parsed_url.hostname)
                port = parsed_url.port
                udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                udp_socket.settimeout(5)

                message = struct.pack('>QII', 0x41727101980,
                                      0, random.randint(0, 500000))

                # Try two times
                done = False
                for i in range(0, 2):
                    if done:
                        break

                    try:
                        udp_socket.sendto(message, (ip_address, port))
                        response = udp_socket.recv(2048)
                        if (message[8:16] == response[0:8]):
                            pass
                        else:
                            print 'Wrong message from tracker'
                            continue
                    except (socket.error, socket.timeout) as err:
                        print 'Could not contact tracker: %s' % err
                        continue

                    # Create the message
                    message = response[8:16] + \
                        struct.pack('>II', 1,
                                    random.randint(0, 500000)) + \
                        info_hash + peer_id + \
                        struct.pack('>QQQIIIih', 0,
                                    length, 0, 0, 0, 0, numwant, port)
                    for j in range(0, 4):
                        try:
                            udp_socket.sendto(message, (ip_address, port))
                            response = udp_socket.recv(2048)
                            if (message[8:16] == response[0:8]):
                                print 'Received Peer Message'
                                done = True
                                #print_escaped_hex(response[20:], True)
                                self.udp_or_http = 'udp'
                                self.cur_url = url
                                return response[20:]
                            else:
                                print 'Wrong message from tracker'
                                continue
                        except (socket.error, socket.timeout) as err:
                            print 'Could not contact tracker: %s' % err
                            continue
                if done:
                    break
                else:
                    # Remove the peer
                    print 'Removing tracker %s' % url
                    self.announce_url.remove(url)

        # for url in self.announce_url:
        #     if 'http://' in url:
        #         if testing:
        #             print 'Sending GET Request to Tracker'
        # Populate the parameters for the URL
        #         params = {'info_hash': str(info_hash),
        #                   'peer_id': peer_id,
        #                   'downloaded': str(downloaded),
        #                   'uploaded': str(uploaded),
        #                   'left': str(length),
        #                   'event': state,
        #                   'port': str(port),
        #                   'corrupt': str(corrupt),
        #                   'key': key,
        #                   'numwant': str(numwant),
        #                   'compact': str(compact),
        #                   'no_peer_id': str(no_peer_id),
        #                   }
        # Send the HTTP GET
        #         try:
        #             response = requests.get(url, params=params, timeout=0.1)
        #             print response.url
        #         except requests.exceptions.RequestException:
        #             continue
        # print response.content
        # Check to see if we get good data back
        #         if response.status_code > 400:
        #             if testing:
        #                 print 'Failed to Connect to Tracker'
        #                 print 'Status Code: %s' % response.status_code
        #                 print 'Reason: %s' % response.reason
        #             ret_val = 0
        #         elif 'peers' not in response.content:
        #             if testing:
        #                 print 'Failed to Connect to Tracker'
        #                 print 'Incorrect URL Parameters'
        #             ret_val = 0
        #         else:
        #             if testing:
        #                 print 'Received GET Response from Tracker'
        #             result = bdecode_data(response.content)
        #             ret_val = result
        #             self.udp_or_http = 'http'
        #             if testing:
        #                 print 'Received Peer Candidate List'
        #         return ret_val
        if testing:
            print 'Tracker must be a GET/UDP tracker'
        ret_val = 0
        return ret_val

    def update_peer_list(self):
        # Connect to the tracker
        peer_data = self.connect_to_tracker(self.data['info_hash'],
                                            self.data['peer_id'],
                                            self.data['file_length'],
                                            self.data['state'],
                                            self.data['port'],
                                            self.data['compact'],
                                            self.data['no_peer_id'],
                                            self.data['key'],
                                            self.piece_mgr.downloaded,
                                            self.piece_mgr.uploaded,
                                            self.piece_mgr.corrupt,
                                            self.peer_mgr.numwant)
        if self.udp_or_http == 'http':
            # We got some peer data back and it's http, let's parse it and
            # give the peers to the peer manager
            if peer_data != 0:
                if isinstance(peer_data['peers'], str):
                    ascii_peer_data = bin2asc(peer_data['peers'])

                    # Each two hex digits counts as one character and there are
                    # 6 characters per host:
                    #       4 characters for ip address and
                    #       2 chars for port
                    #
                    # So to get the number of peers we would divide the
                    # length of the peer data we get back by 6.
                    #
                    # Since we are actually writing
                    # out the two hex digits we have
                    # to divide by 12 because now one
                    # hex digit = one character

                    num_peers = len(ascii_peer_data) / 12

                    if testing:
                        print ''

                    # Send it off to Peer Manager to fix
                    return [num_peers, ascii_peer_data]
                else:
                    print "Tracket gave back bad data"
                    self.announce_url.remove(self.cur_url)
            else:
                assert peer_data != 0, \
                    "Tracker gave back bad data"
        else:
            # We got udp data back
            if peer_data != 0:
                ascii_peer_data = bin2asc(peer_data)

                num_peers = len(ascii_peer_data) / 12
                print num_peers

                if testing:
                    print ''

                print ascii_peer_data
                # Send it off to Peer Manager to fix
                return [num_peers, ascii_peer_data]
            else:
                print "Tracker gave back bad data"
                self.announce_url.remove(self.cur_url)
