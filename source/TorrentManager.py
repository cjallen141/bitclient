# TorrentManager.py
from TrackerManager import TrackerManager


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

        #self.comment = data['comment']
        self.announce_url = data['announce']
        self.piece_length = data['info']['piece length']

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

    # Methods
    def initialize_subordinates(self):
        self.TrackM1 = TrackerManager(self.announce_url)

    def kill_subordinates(self):
        if hasattr(self, 'TrackM1'):
            del self.TrackM1

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
