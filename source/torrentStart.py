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
    peer_id = 'ThisIsATestOfGTENS00'
    key = '50EDCACE'
    port = 61130
    compact = 1
    no_peer_id = 1

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

    # Now we can start the TorrentManager
    TorM1 = TorrentManager(data)

    # Initialize its subordinates
    TorM1.initialize_subordinates()

    # Connect to the tracker
    peer_data = TorM1.TrackM1.connect_to_tracker(TorM1.info_hash,
                                                 TorM1.peer_id,
                                                 TorM1.length,
                                                 TorM1.PieceM1.downloaded,
                                                 TorM1.PieceM1.uploaded,
                                                 TorM1.state,
                                                 TorM1.port,
                                                 TorM1.PieceM1.corrupt,
                                                 TorM1.key,
                                                 TorM1.PeerM1.numwant,
                                                 TorM1.compact,
                                                 TorM1.no_peer_id)
    if peer_data != 0:
        Decoder.print_hex(peer_data['peers'])
        print len(peer_data['peers'])/6
    else:
        exit_grace(TorM1)


def exit_grace(TorM1):
    # Kill the subordinates and then the Torrent Manager
    TorM1.kill_subordinates()
    print 'Killing Torrent Manager...',
    del TorM1
    print 'Killed'
    print 'Goodbye'

if __name__ == '__main__':
    main()
