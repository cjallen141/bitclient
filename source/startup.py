# startup file this just calls the main_loop() function in torrentStart.py
from torrentStart import main_loop

file1 = '../referenceFiles/TestTorrent.torrent'
file2 = '../referenceFiles/WhySoccerMatters-Original.torrent'
file3 = 'ThisIsNotARealFile.torrent'
file4 = '/Users/brent/Downloads/ubuntu-13.10-desktop-amd64.iso.torrent'
file5 = '/Users/brent/Downloads/t-rice.jpg.torrent'
file6 = '/Users/brent/Downloads/ProGit.pdf.torrent'


peer_id = 'ThisIsATestOfGTENS00'
key = '50EDCACE'
port = 61130
compact = 1
no_peer_id = 1

main_loop(file4, peer_id, key, port, compact, no_peer_id)
