# TorrentManager.py
from TrackerManager import TrackerManager
from peermanager import PeerManager


class TorrentManager:
    # Attributes

    # Constructors
    def __init__(self, data):
        # We have the data, fill in the relevant fields
        # Mandatory Fields
        #   announce-url
        #   info (dictionary)
        #       piece length
        #       name
        #       pieces
        #       path
        #       length
        # All others are optional

        print 'Initializing Torrent Manager...',
        #self.comment = data['comment']
        self.info_hash = data['info_hash']
        self.announce_url = data['announce']
        self.piece_length = data['info']['piece length']
        self.peer_id = data['peer_id']

        # Check to see if it is a multi-file torrent or a single-file torrent
        # Multi File
        if 'files' in data['info']:
            self.multi_file = True
            self.files = data['info']['files']

            # Run through and extract files and put them into

        # Single File
        else:
            self.multi_file = False
            self.name = data['info']['name']
            self.length = data['info']['length']

        print 'Initialized'

    # Methods
    def initialize_subordinates(self):
        data = [self.announce_url, self.info_hash, self.peer_id]
        print 'Initializing Tracker Manager...',
        self.TrackM1 = TrackerManager(data)
        print 'Initialized'
        print 'Initializing Peer Manager...',
        self.PeerM1 = PeerManager(self.peer_id, self.TrackM1)
        print 'Initialized'
        print ''

    def kill_subordinates(self):
        print ''
        if hasattr(self, 'TrackM1'):
            print 'Killing Tracker Manager...',
            del self.TrackM1
            print 'Killed'
        if hasattr(self, 'PeerM1'):
            print 'Killing Peer Manager...',
            del self.PeerM1
            print 'Killed'

## Testing Code
# file = '../referenceFiles/TestTorrent.torrent'
# file1 = '../referenceFiles/WhySoccerMatters-Original.torrent'
# fh = open(file, 'rb')
# fh1 = open(file1, 'rb')
# encodedData = fh.read()
# encodedData1 = fh1.read()
# fh.close()
# fh1.close()
# decodedData = bencode.bdecode(encodedData)
# decodedData1 = bencode.bdecode(encodedData1)

# TM1 = TorrentManager(decodedData)
# #print TM1.comment
# print TM1.announce_url
# print TM1.name
# if (TM1.multi_file is True):
#     print TM1.files
# else:
#     print TM1.length

# TM2 = TorrentManager(decodedData1)
# print TM2.announce_url
# print TM2.name
# if (TM2.multi_file is True):
#     print TM2.files
# else:
#     print TM2.length
