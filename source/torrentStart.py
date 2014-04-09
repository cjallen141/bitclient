# This is all the code that is run to start the torrent manager

import Decoder
from TorrentManager import TorrentManager

# The first thing we want to do is have them input a file
# For now this is just going to be hard-coded in
# 	because I don't want to have to input everytime
# file1 is a single-file torrent
# file2 is a multi-file torrent
file1 = '../referenceFiles/TestTorrent.torrent'
file2 = '../referenceFiles/WhySoccerMatters-Original.torrent'
file3 = 'ThisIsNotARealFile.torrent'

# Next we decode it
data = Decoder.decodeTorrent(file2)

# Now we can start the TorrentManager
TorM1 = TorrentManager(data)

# Initialize its subordinates
TorM1.initialize_subordinates()

# Connect to the tracker
TorM1.TrackM1.connect_to_tracker()

# Kill the subordinates and then the Torrent Manager
TorM1.kill_subordinates()
del TorM1