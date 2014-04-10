# This is all the code that is run to start the torrent manager

import Decoder
import hashlib
from TorrentManager import TorrentManager

# The first thing we want to do is have them input a file
# For now this is just going to be hard-coded in
#   because I don't want to have to input everytime
# file1 is a single-file torrent
# file2 is a multi-file torrent
file1 = '../referenceFiles/TestTorrent.torrent'
file2 = '../referenceFiles/WhySoccerMatters-Original.torrent'
file3 = 'ThisIsNotARealFile.torrent'
peer_id = 2231

# Next we decode it
data = Decoder.decode_torrent(file1)

# Get the SHA1 Hash for the info dictionary
info = data['info']
bencoded_info = Decoder.encode_info(info)
info_hash = hashlib.sha1(bencoded_info).digest()
Decoder.print_hash(info_hash)

# Add our peer id and hash to the dictionary
data['peer_id'] = peer_id
data['info_hash'] = info_hash

# Now we can start the TorrentManager
TorM1 = TorrentManager(data)

# Initialize its subordinates
TorM1.initialize_subordinates()

# Connect to the tracker
#TorM1.TrackM1.connect_to_tracker(TorM1.info_hash,
#                                 TorM1.peer_id,
#                                 TorM1.piece_length)

# Kill the subordinates and then the Torrent Manager
TorM1.kill_subordinates()
print 'Killing Torrent Manager...'
del TorM1
print 'Killed'
print 'Goodbye'
