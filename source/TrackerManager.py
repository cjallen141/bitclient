# Tracker Manager Class
import requests
import Decoder


class TrackerManager:
    # Attributes
    # Constructors
    def __init__(self, data):
        self.announce_url = data[0]

    # Methods
    def connect_to_tracker(self, info_hash, peer_id, piece_length):
        print 'Sending GET Request to Tracker'

        params = {'info_hash': info_hash,
                  'peer_id': peer_id,
                  'left': piece_length}

        print params
        print self.announce_url
        response = requests.get(self.announce_url, params=params)
        print response.content
        result = Decoder.decode_info(response.content)
        print result

        if response.status_code > 400:
            print 'Failed to Connect to Tracker'
            print 'Status Code: %s' % response.status_code
            print 'Reason: %s' % response.reason
        return
# Testing Code
