from Queue import Queue
import Decoder 
import sys

class PieceManager:
	# Attributes
    # Constructors
    def __init__(self, piece_byte_length):

    	self.PIECE_HASH_LENGTH = 20 #the length of the hash for the piece
    								# should always be a 20byte number
        self.piece_byte_length = piece_byte_length #total number of bytes in a piece 
        self.downloaded = 0
        self.uploaded = 0
        self.corrupt = 0

        self.piece_list = [] #used to initially hold all the pieces. during normal mode, this will be empty
        self.num_of_pieces = 0

        self.desired_piece_q = Queue() #holds all the currently desired pieces. 
        
        self.downloaded_piece_list = [] #list of completed downloaded pieces.This should be kept
        								#ordered by the piece index
        self.downloaded_piece_q = Queue() #queue of downloaded pieces from peers
    # Methods
    def is_finished_downloading(self):
    	pass
    	#check if the file is completely downloaded

    def read_piece_list(self, hash_piece_list):
        #this will parse the piece_list given to it by the trackermanager
        #
    	assert (len(hash_piece_list) % self.PIECE_HASH_LENGTH == 0 ), \
    	 "Check piece list size. Must be equal to piece_byte_length"
    	x=0
    	idx=0
    	while(x< (len(hash_piece_list))):
    	    #iterate over the hash string and extract out the hashes
    		#popluates the piece_list list with piece objects
    		self.piece_list.append(Piece(idx, hash_piece_list[x:(x+self.PIECE_HASH_LENGTH-1)]))
    		self.num_of_pieces = self.num_of_pieces + 1
    		
       		x = x+self.PIECE_HASH_LENGTH
       		idx=idx+1 #increment piece index

       	#sanity check to make sure that is always correct	
       	assert len(self.piece_list) is len(hash_piece_list)/self.PIECE_HASH_LENGTH , \
       		"the piece list doesn't have the correct number of pieces"

    def gen_desired_piece_q(self):
    	#explicitly removing the piece from self.pieces and putting it into the desired queue
    	assert len(self.piece_list) != 0 , \
    		"piece list is empty, something went wrong"

    	print 'generating desired piece q..'
    	while len(self.piece_list) > 0:

    		piece = self.piece_list.pop(0)
    		print piece
    		self.desired_piece_q.put(piece)
    	return self.desired_piece_q

    def print_progress(self):
    	#print the current progress of the file. This will be helpful for debugging and using the 
    	#program visually
    		out = list('\rDownloaded Pieces: |')
    		idx = len(out)
    		
    		x = range(0,self.num_of_pieces)
    		for i in x:
    			out.extend('_l')

    		for piece in self.downloaded_piece_list:

    			offset = piece.idx
    			out[(idx)+offset*2] = '#'
    		sys.stdout.write("".join(out))
    		sys.stdout.flush()
    		#may want to move the actual printing to another function if want to format a bunch together
    		#the output looks like this: 'Downloaded Pieces: |_|_|_|#|#|....' where the #'s are downloaded

class Piece:
	# Attributes

	# Constructors
	def __init__(self,idx, hash):
		self.idx = idx
		self.hash = hash
		self.downloaded = False #indicates if all the data for the Piece has been downloaded
		self.verified = False 	#indicates if the Piece has been successfully verified with hash
		self.loaded = False		#indicates if piece is currently loaded in mem

		self.data = []
		self.block_offset = 0 
		self.block_length = 16384
	def __str__(self):
		#prints out the piece. <idx>: <hash> 
		out = 'Piece idx: ' + str(self.idx) + ' Hash: ' + str(self.hash) + ' DL: ' + str(self.downloaded) \
		+ ' Ver: ' + str(self.verified)
		return out


	#Properties

	def block_offset():
	    doc = "The block_offset property."
	    def fget(self):
	        return self._block_offset
	    def fset(self, value):
	        self._block_offset = value
	    def fdel(self):
	        del self._block_offset
	    return locals()
	block_offset = property(**block_offset())

	def block_length():
	    doc = "The block_length property."
	    def fget(self):
	        return self._block_length
	    def fset(self, value):
	        self._block_length = value
	    def fdel(self):
	        del self._block_length
	    return locals()
	block_length = property(**block_length())


	# Methods
	def verify_piece(self):
		#attempts to verify the piece against its hash value. returns boolean of result
		#will also set the verified to 1 

		#check if it is even all here
		if not self.downloaded:
			return 0
		#check against SHA1 hash. TODO
		hash_of_data = Decoder.create_hash(self.data)

		if hash_of_data == self.hash:
			self.verified = True
			print self
			return 1
		else:
			return 0




###testing 
if __name__ == '__main__':
	pm = PieceManager(16384)

	pm.read_piece_list("Itshouldbetwentybit_Itshouldbetwentybit_Itshouldbetwentybit_Itshouldbetwentybit_")


	piece_q = pm.gen_desired_piece_q()

	while piece_q.empty() ==0:
		piece = piece_q.get()

		print piece

	piece.block_offset = 2
	print piece.block_offset
	print 'local queue: ' + str(piece_q.empty() )
	print 'PM queue: ' + str(pm.desired_piece_q.empty())

	x = range(0,4)
	for i in x:
		pm.downloaded_piece_list.append(Piece(i,"itshouldbetwentybits"))
		pm.print_progress()
		d = 0
		while (d<1000000):
			d += 1

	sys.stdout.write('\n')
	pm.downloaded_piece_list[0].hash = Decoder.create_hash('itshouldbetwentybits')
	pm.downloaded_piece_list[0].data = 'itshouldbetwentybits'
	pm.downloaded_piece_list[0].downloaded = True

	print pm.downloaded_piece_list[0]

	pm.downloaded_piece_list[0].verify_piece()