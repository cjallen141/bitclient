# TorrentManager.py
from TrackerManager import TrackerManager
from peermanager import PeerManager
from PieceManager import PieceManager


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

        # Some Attributes being populated
        #self.comment = data['comment']
        self.info_hash = data['info_hash']
        self.announce_url = data['announce']
        self.piece_length = data['info']['piece length']
        self.peer_id = data['peer_id']
        self.state = 'started'
        self.key = data['key']
        self.port = data['port']
        self.compact = data['compact']
        self.no_peer_id = data['no_peer_id']

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
    # Initialize all of the Managers
    def initialize_subordinates(self):
        data = [self.announce_url, self.info_hash, self.peer_id]
        print 'Initializing Tracker Manager...',
        self.TrackM1 = TrackerManager(data)
        print 'Initialized'
        print 'Initializing Peer Manager...',
        self.PeerM1 = PeerManager(self.peer_id)
        print 'Initialized'
        print 'Initializing Piece Manager...',
        self.PieceM1 = PieceManager(self.piece_length)
        print 'Initialized'
        print ''
        self.TrackM1.PeerM1 = self.PeerM1
        self.TrackM1.PieceM1 = self.PieceM1
        self.PeerM1.TrackM1 = self.TrackM1
        self.PeerM1.PieceM1 = self.PieceM1
        self.PieceM1.TrackM1 = self.TrackM1
        self.PieceM1.PeerM1 = self.PeerM1
        self.TrackM1.TorM1 = self
        self.PieceM1.TorM1 = self
        self.PeerM1.TorM1 = self

    # Kill all of the Managers
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
        if hasattr(self, 'PieceM1'):
            print 'Killing Piece Manager...',
            del self.PieceM1
            print 'Killed'

## Testing Code
