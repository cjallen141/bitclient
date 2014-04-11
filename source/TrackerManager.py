# Tracker Manager Class
import requests
import Decoder


class TrackerManager:
    # Attributes
    # Constructors
    def __init__(self, data):
        self.announce_url = data[0]

    # Methods
    def connect_to_tracker(self, info_hash, peer_id, length,
                           downloaded, uploaded, state, port,
                           corrupt, key, numwant, compact,
                           no_peer_id):
        print 'Sending GET Request to Tracker'
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
        response = requests.get(self.announce_url, params=params)
        #print response.url
        #print response.content

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
            print result
            ret_val = result
        return ret_val

    def update_peer_list(self):
        print 'Updating list of peers...'
        return ['peer_1', 'peer_2', 'peer_3']


# Testing Code
