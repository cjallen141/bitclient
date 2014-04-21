# TorrentManager.py
from Decoder import *
from TrackerManager import TrackerManager
from peermanager import PeerManager
from PieceManager import PieceManager
import time
import threading


def main():

    print 'Initializing Torrent Manager...',

    data = {}

    # The first thing we want to do is have them input a file
    # For now this is just going to be hard-coded in
    #   because I don't want to have to input everytime
    # file1 is a single-file torrent
    # file2 is a multi-file torrent
    #file1 = '../referenceFiles/TestTorrent.torrent'
    #file1 = '../referenceFiles/WhySoccerMatters-Original.torrent'
    #file1 = 'ThisIsNotARealFile.torrent'
    #file1 = '/Users/brent/Downloads/ubuntu-13.10-desktop-amd64.iso.torrent'
    #file1 = '/Users/brent/Downloads/t-rice.jpg.torrent'
    file1 = '/Users/brent/Downloads/ProGit.pdf.torrent'

    data['write_file'] = './ubuntu-13.10-desktop-amd64.iso'
    data['torrent_file'] = file1
    data['peer_id'] = 'ThisIsATestOfGTENS00'
    data['key'] = '50EDCACE'
    data['port'] = 61130
    data['compact'] = 1
    data['no_peer_id'] = 1
    data['max_connections'] = 5
    data['state'] = 'started'
    data['numwant'] = 5

    # Next we decode it
    # decoded_data is the data from the torrent file.
    # we will separate everything and put it into a data
    # structure so that we don't have to do things like
    # decoded_data['info']['piece length'] and we can
    # do things like data['piece_length']
    decoded_data = bdecode_torrent(data['torrent_file'])
    #print decoded_data
    #print decoded_data

    # Get the SHA1 Hash for the info dictionary
    # It has to be bencoded first
    info = decoded_data['info']
    info = bencode_data(info)
    info_hash = create_hash(info)

    # Add our stuff to the data structure
    data['info_hash'] = info_hash
    data['piece_length'] = decoded_data['info']['piece length']
    data['announce'] = decoded_data['announce']

    # Check to see if it is a multi-file torrent or a single-file torrent
    # Multi File
    if 'files' in decoded_data['info']:
        data['multi_file'] = True
        #data['files'] = decoded_data['info']['files']

        # Run through and extract files and put them into a data structure
        pass

    # Single File
    else:
        data['multi_file'] = False
        data['file_name'] = decoded_data['info']['name']
        data['length'] = decoded_data['info']['length']
        data['pieces_hash'] = decoded_data['info']['pieces']

    print 'Initialized'

    print 'Initializing Tracker Manager...',
    TrackM = TrackerManager(data)
    print 'Initialized'
    print 'Initializing Peer Manager...',
    PeerM = PeerManager(data)
    print 'Initialized'
    print 'Initializing Piece Manager...',
    PieceM = PieceManager(data)
    print 'Initialized'
    print ''

    TrackM.peer_mgr = PeerM
    TrackM.piece_mgr = PieceM
    PeerM.track_mgr = TrackM
    PeerM.piece_mgr = PieceM
    PieceM.track_mgr = TrackM
    PieceM.peer_mgr = PeerM

    # Once this Peer Manager is spawned, this MainThread will stop
    # Calling 'print threading.enumerate() will output this:'
    # [<_MainThread(MainThread, stopped 140735224099600)>
    #  , <PeerManager(Thread-1, started 4568743936)>]
    PeerM.start()

    for i in range(0, 300):
        time.sleep(.05)
        print threading.enumerate()

if __name__ == "__main__":
    main()
