# This is all the code that is run to start the torrent manager

import Decoder
from TorrentManager import TorrentManager


def main_loop(file1, peer_id, key, port, compact, no_peer_id):
    # The first thing we want to do is have them input a file
    # For now this is just going to be hard-coded in
    #   because I don't want to have to input everytime
    # file1 is a single-file torrent
    # file2 is a multi-file torrent

    # Next we decode it
    data = Decoder.bdecode_torrent(file1)

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

    TorM1.PeerM1.update_peer_list()


# Exit the program gracefully (hopefully)
def exit_grace(TorM1):
    # Kill the subordinates and then the Torrent Manager
    TorM1.kill_subordinates()
    print 'Killing Torrent Manager...',
    del TorM1
    print 'Killed'
    print 'Goodbye'
