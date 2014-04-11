from Queue import Queue
import Decoder 

class PieceManager:
	#PIECE_HASH_LENGTH = 20
    # Attributes
    # Constructors
    def __init__(self, piece_byte_length):

    	self.PIECE_HASH_LENGTH = 20 #the length of the hash for the piece
    								# should always be a 20byte number


        self.piece_byte_length = piece_byte_length #total number of bytes in a piece 
        self.downloaded = 0
        self.uploaded = 0
        self.corrupt = 0

        self.piece_list = []
        self.desired_piece_q = Queue()
    # Methods

    def read_piece_list(self, hash_piece_list):
        #this will parse the piece_list given to it by the trackermanager
        

    	assert (len(hash_piece_list) % self.PIECE_HASH_LENGTH == 0 ), \
    	 "Check piece list size. Must be equal to piece_byte_length"
    	x=0
    	idx=0
    	while(x< (len(hash_piece_list))):
    	    #iterate over the hash string and extract out the hashes
    		#popluates the piece_list list with piece objects
    		self.piece_list.append(Piece(idx, hash_piece_list[x:(x+self.PIECE_HASH_LENGTH-1)]))
    		
    		
       		x = x+self.PIECE_HASH_LENGTH
       		idx=idx+1 #increment piece index

       	#sanity check to make sure that is always correct	
       	assert len(self.piece_list) is len(hash_piece_list)/self.PIECE_HASH_LENGTH , \
       		"the piece list doesn't have the correct number of pieces"
    	


class Piece:
	# Attributes

	# Constructors
	def __init__(self,idx, hash):
		self.idx = idx
		self.hash = hash
		self.downloaded = 0
		self.verified = 0 

	def __str__(self):
		#prints out the piece. <idx>: <hash> 
		out = str(self.idx) + ': ' + str(self.hash)
		return out
	# Methods



class Block:
	# Attributes

	# Constructors
	def __init__(self):
		print 'created a new block'

	# Methods

###testing 
if __name__ == '__main__':
	pm = PieceManager(16)

	pm.read_piece_list("Itshouldbetwentybit_Itshouldbetwentybit_Itshouldbetwentybit_Itshouldbetwentybit_")

