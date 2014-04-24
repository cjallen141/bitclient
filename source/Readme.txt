In order to run this project, you need to have:
	BitTorrent-bencode 5.0.8.1
		https://pypi.python.org/pypi/BitTorrent-bencode/5.0.8.1
	Requests
		http://docs.python-requests.org/en/latest/
	BitString
		https://code.google.com/p/python-bitstring/

Once these are all installed, unzip all the files in the .zip archive into one folder. 

General
--------

Then follow these steps:

	1) Go into the folder with the source code
	2) Find a small (very small or it will take forever) torrent with UDP or HTTP trackers
	3) Move the torrent file into a place where you know, we usually just put it into the source
		folder.
	4) Open up uTorrent, or any other bittorrent client
	5) Open the torrent file and let it fully download, wait for it to start seeding.
	6) Go into uTorrent settings and figure out what port number the client is using
	7) Look at the PeerManager.py file and on Line 77 change the port number from 61137 to the port
		that was found from uTorrent
	8) Run this command in Terminal

		python TorrentManager.py -f <file-path-and-name>

	9) This should output a file in the same directory. 

Here is a list of Torrent files, and where to find them, that we have gotten to work with our client. 

	Jason Derulo - Talk Dirty.mp3
		http://kickass.to/jason-derulo-talk-dirty-feat-2-chainz-2013-single-t7685250.html
	Ellie Goulding - Burn.mp3
		http://www.torrentlookup.com/torrent/ellie-goulding-burn-mp3/FtGH/
	Ubuntu 13.10 AMD64
		http://torrent.ubuntu.com:6969/

Problems
--------

When writing the code, we were able to implement all of the requirements for a grade of
100 on the project. We also tried to implement many of the extra credit parts but ran 
into several bugs that caused us to not be able to run the code fully all the time. 
Below is a list of all the requirements and extras that we did. In the run that you 
did above, you can see us parse the torrent, hash the info directory from the torrent
file, handshake with a peer (ourselves), parse the messages and send requests, receive
blocks, and comine and verify the file. 


To see that we implemented all the extras that we said we did, you can follow these steps.

1) Go into the folder with the source code
2) Find a small (very small or it will take forever) torrent with UDP or HTTP trackers
3) Move the torrent file into a place where you know, we usually just put it into the 
	source folder.
4) Look at the PeerManager.py file and comment out Lines 75-85. Uncomment Lines 87-131
5) Run this command

	python TorrentManager.py -f <file-path-and-name>

6) This may or may not work fully, it might hang for reasons i'll talk about later


Bugs That Caused the Torrent Program to Fail With the Extras
------------------------------------------------------------
1) We are able to connect to multiple peers but sometimes, after sending us many pieces, they will timeout
	or not have anymore pieces that we need. When this happens, the thread for this peer will end but the
	peer manager won't know so it won't connect to any new peers. If none of the peers that we are currently
	connected to have any pieces to give us, they will all shut down. The bug is that peer manager won't know
	and will keep on going, thinking that we have peers still running. 

2) For some reason, we stop sending and receiving messages and just go into an infinite loop checking whether
	we are finished or not. I haven't found the source of this problem but it only happens when we are
	connecting to peers other than ourself. 


Requirements that we implemented and Extras
-------------------------------------------
The requirements and extras are listed below with a 1) Works, 2) Doesn't Work, or 3) Falls in Between

Test these by running the General steps specified above
	1) Parse Torrent (Works)
	2) Hash/Handshake (Works)
	3) Parse Message (Works)
	4) Request (Works)
	5) Receive Blocks (Works)
	6) Combine + Verify (Works)

Test these by running the Problem steps specified above
	1) Contact the tracker and get peers back (Works)
	2) Connect and Recieve from Multiple Peers (Works)
	3) Use threading (Peer Manager is a thread along with Peers) (Fall in Between)

Overall: (Works)

Overall, I would say that every part of our project works. There are a couple of bugs that we would be able to
work out if we had a couple more days to work with this. 
