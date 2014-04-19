# This is all the code that is run to start the torrent manager

import Decoder
from TorrentManager import TorrentManager


def main():
    # The first thing we want to do is have them input a file
    # For now this is just going to be hard-coded in
    #   because I don't want to have to input everytime
    # file1 is a single-file torrent
    # file2 is a multi-file torrent
    #file1 = '../referenceFiles/TestTorrent.torrent'
    #file2 = '../referenceFiles/WhySoccerMatters-Original.torrent'
    #file3 = 'ThisIsNotARealFile.torrent'
    file4 = '/Users/brent/Downloads/ubuntu-13.10-desktop-amd64.iso.torrent'
    #file5 = '/Users/brent/Downloads/t-rice.jpg.torrent'
    #file6 = '/Users/brent/Downloads/ProGit.pdf.torrent'

    peer_id = 'ThisIsATestOfGTENS00'
    key = '50EDCACE'
    port = 61130
    compact = 1
    no_peer_id = 1
    max_connections = 1

    # Next we decode it
    data = Decoder.bdecode_torrent(file4)

    # Get the SHA1 Hash for the info dictionary
    # It has to be bencoded first
    info = data['info']
    info = Decoder.bencode_data(info)
    info_hash = Decoder.create_hash(info)

    # Add our peer id and hash to the dictionary
    data['peer_id'] = peer_id
    data['info_hash'] = info_hash
    data['port'] = port
    data['key'] = key
    data['compact'] = compact
    data['no_peer_id'] = no_peer_id
    data['max_connections'] = max_connections

    # Now we can start the TorrentManager
    TorM1 = TorrentManager(data)

    # Initialize its subordinates
    TorM1.initialize_subordinates()
    TorM1.PeerM1.update_peer_list()
    TorM1.PeerM1.connect_to_peers()

    print ''
    print 'Killed Tracker Manager...'
    print 'Killed Peer Manager...'
    print 'Killed Piece Manager...'
    print 'Killed Torrent Manager...'

if __name__ == "__main__":
    main()
