# TorrentManager.py
from Decoder import *
from TrackerManager import TrackerManager
from peermanager import PeerManager
from PieceManager import PieceManager
import os
#import time
#import threading


def main():

    # use this to enable/disable all the other printing

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
    file1 = '/Users/brent/Downloads/ubuntu-13.10-desktop-amd64.iso.torrent'
    #file1 = '/Users/brent/Downloads/t-rice.jpg.torrent'
    #file1 = '../referenceFiles/ProGit.pdf.torrent'
    #file1 = '/Users/brent/Downloads/test.torrent'

    data['torrent_file'] = file1
    data['output_path'] = '/Users/brent/Documents'
    data['peer_id'] = 'ThisIsATestOfGTENS00'
    #data['key'] = '50EDCACE'
    data['key'] = 'A89BA1C1'
    data['port'] = 61130
    data['compact'] = 1
    data['no_peer_id'] = 1
    data['max_connections'] = 10
    data['state'] = 'started'
    data['numwant'] = 20
    data['file_name'] = []
    data['length'] = []
    data['file_length'] = 0

    # Next we decode it
    # decoded_data is the data from the torrent file.
    # we will separate everything and put it into a data
    # structure so that we don't have to do things like
    # decoded_data['info']['piece length'] and we can
    # do things like data['piece_length']
    decoded_data = bdecode_torrent(data['torrent_file'])
    # print decoded_data
    # print decoded_data

    # Get the SHA1 Hash for the info dictionary
    # It has to be bencoded first
    info = decoded_data['info']
    info = bencode_data(info)
    info_hash = create_hash(info)

    # Add our stuff to the data structure
    data['info_hash'] = info_hash
    data['piece_length'] = decoded_data['info']['piece length']
    data['announce'] = decoded_data['announce']
    data['pieces_hash'] = decoded_data['info']['pieces']
    data['name'] = decoded_data['info']['name']

    # Check to see if it is a multi-file torrent or a single-file torrent
    # Multi File
    if 'files' in decoded_data['info']:
        data['multi_file'] = True
        data['path'] = data['output_path'] + os.sep + \
            decoded_data['info']['name'] + os.sep

        # Each file name is actually a path
        for one_file in decoded_data['info']['files']:
            file_name = one_file['path'][0]
            data['file_name'].append(file_name)
            data['length'].append(one_file['length'])
            data['file_length'] = data['file_length'] + one_file['length']

    # Single File
    else:
        data['multi_file'] = False
        data['file_name'] = decoded_data['info']['name']
        data['path'] = data['output_path'] + os.sep
        data['length'] = decoded_data['info']['length']
        data['file_length'] = data['length']

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
    # , <PeerManager(Thread-1, started 4568743936)>]
    PeerM.start()

if __name__ == "__main__":

    main()
