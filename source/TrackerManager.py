# Tracker Manager Class
from Decoder import *
import requests

testing = False

class TrackerManager:
    # Attributes

    # Constructors
    def __init__(self, data):
        self.data = data
        self.announce_url = data['announce']

        self.peer_mgr = ''
        self.piece_mgr = ''

    # Methods
    def connect_to_tracker(self, info_hash, peer_id, length,
                           state, port, compact, no_peer_id,
                           key, downloaded, uploaded, corrupt,
                           numwant):

        if 'http://' in self.announce_url:
            if testing:
                print 'Sending GET Request to Tracker'
            # Populate the parameters for the URL
            params = {'info_hash': str(info_hash),
                      'peer_id': peer_id,
                      'downloaded': str(downloaded),
                      'uploaded': str(uploaded),
                      'left': str(length),
                      'event': state,
                      'port': str(port),
                      'corrupt': str(corrupt),
                      'key': key,
                      'numwant': str(numwant),
                      'compact': str(compact),
                      'no_peer_id': str(no_peer_id),
                      }

            # Send the HTTP GET
            response = requests.get(self.announce_url, params=params)
            #print response.url
            #print response.content

            # Check to see if we get good data back
            if response.status_code > 400:
                if testing:
                    print 'Failed to Connect to Tracker'
                    print 'Status Code: %s' % response.status_code
                    print 'Reason: %s' % response.reason
                ret_val = 0
            elif 'peers' not in response.content:
                if testing:
                    print 'Failed to Connect to Tracker'
                    print 'Incorrect URL Parameters'
                ret_val = 0
            else:
                if testing:
                    print 'Received GET Response from Tracker'
                result = bdecode_data(response.content)
                ret_val = result
                if testing:
                    print 'Received Peer Candidate List'
            return ret_val
        else:
            if testing:
                print 'Tracker must be a GET tracker'
            ret_val = 0
            return ret_val

    def update_peer_list(self):
        # Connect to the tracker
        peer_data = self.connect_to_tracker(self.data['info_hash'],
                                            self.data['peer_id'],
                                            self.data['length'],
                                            self.data['state'],
                                            self.data['port'],
                                            self.data['compact'],
                                            self.data['no_peer_id'],
                                            self.data['key'],
                                            self.piece_mgr.downloaded,
                                            self.piece_mgr.uploaded,
                                            self.piece_mgr.corrupt,
                                            self.peer_mgr.numwant)

        # We got some peer data back, let's parse it and
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
                # Since we are actually writing out the two hex digits we have
                # to divide by 12 because now one hex digit = one character

                num_peers = len(ascii_peer_data)/12

                if testing:
                    print ''

                # Send it off to Peer Manager to fix
                return [num_peers, ascii_peer_data]
            else:
                pass
        else:
            assert peer_data != 0, \
                "Tracker gave back bad data"

# Testing Code
