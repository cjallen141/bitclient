# Tracker Manager Class
import requests
import Decoder
import torrentStart


class TrackerManager:
    # Attributes

    # Constructors
    def __init__(self, data):
        self.announce_url = data[0]

        self.PeerM1 = ''
        self.PieceM1 = ''

    # Methods
    def connect_to_tracker(self, info_hash, peer_id, length,
                           downloaded, uploaded, state, port,
                           corrupt, key, numwant, compact,
                           no_peer_id):

        if 'http://' in self.announce_url:
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
                print 'Failed to Connect to Tracker'
                print 'Status Code: %s' % response.status_code
                print 'Reason: %s' % response.reason
                ret_val = 0
            elif 'peers' not in response.content:
                print 'Failed to Connect to Tracker'
                print 'Incorrect URL Parameters'
                ret_val = 0
            else:
                print 'Connected to Tracker'
                result = Decoder.bdecode_data(response.content)
                ret_val = result
                print 'Received Peer List'
            return ret_val
        else:
            print 'Tracker must be a GET tracker'
            ret_val = 0
            return ret_val

    def update_peer_list(self):
        # Connect to the tracker
        peer_data = self.connect_to_tracker(self.TorM1.info_hash,
                                            self.TorM1.peer_id,
                                            self.TorM1.length,
                                            self.PieceM1.downloaded,
                                            self.PieceM1.uploaded,
                                            self.TorM1.state,
                                            self.TorM1.port,
                                            self.PieceM1.corrupt,
                                            self.TorM1.key,
                                            self.PeerM1.numwant,
                                            self.TorM1.compact,
                                            self.TorM1.no_peer_id)

        # We got some peer data back, let's parse it and
        # give the peers to the peer manager
        if peer_data != 0:
            if isinstance(peer_data['peers'], str):
                ascii_peer_data = Decoder.bin2asc(peer_data['peers'])

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

                # Send it off to Peer Manager to fix
                return [num_peers, ascii_peer_data]
            else:
                pass
        else:
            # If we don't get anything back from the tracker then
            # we can't really go any further
            torrentStart.exit_grace(self.TorM1)

# Testing Code
