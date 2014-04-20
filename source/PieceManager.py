from Queue import Queue
import Decoder 
import sys
import os
from bitstring import BitArray
import math 
import struct


PIECE_HASH_LENGTH = 20 		#number of bytes per piece in the hash list
#BLOCK_SIZE = 2**14
BLOCK_SIZE = 2**14 				#size in bytes of a block
###############################################################
class PieceManager:
	# INTERFACE
	#
	#variables:
	#
	#	desired_piece_q  	-Queue that holds all the currently desired pieces
	#	downloaded_piece_q	-Queue to PUT downloaded pieces after completed download of pieces
	#	num_of_pieces		- total number of pieces
	#	f 					-file to write data to 
	#	
	#methods:
	#
	#	is_finished_downloading() -checks if the file has been completely downloaded
	#
	#	print_progress() 		-prints the current downloaded piece list with missing spaces for
	#								pieces not downloaded
    # Constructors
    def __init__(self, file_info, piece_byte_length, hash_piece_list, total_length):

        self.piece_byte_length = piece_byte_length #total number of bytes in a piece 
        self.total_length = total_length #total length of the file in bytes
        self.downloaded = 0
       	self.hash_piece_list = hash_piece_list
       	self.file_info = file_info #
       	self.num_of_pieces = 0

        self.piece_list = [] #used to initially hold all the pieces. during normal mode, this will be empty

       	self.generate_piece_list()
       	##self.read_piece_list(self.hash_piece_list)


        self.desired_piece_q = Queue() #holds all the currently desired pieces. 
        
        self.downloaded_piece_list = [] #list of completed downloaded pieces.This should be kept
        								#     ordered by the piece index
        self.downloaded_piece_q = Queue() #queue of downloaded pieces from peers


       # f=open(file_info['file_name'],'a+')


    # Methods
 
    def is_finished_downloading(self):
    	pass
    	#check if the file is completely downloaded

    def generate_piece_list(self):
        #this will parse the piece_list given to it by the tracker manager
        #
    	assert (len(self.hash_piece_list) % PIECE_HASH_LENGTH == 0 ), \
    	 "Check piece list size. Must be equal to piece_byte_length"
    	x=0
    	idx=0
    	while(x< (len(self.hash_piece_list))):
    	    #iterate over the hash string and extract out the hashes
    		#populates the piece_list list with piece objects
    		self.piece_list.append(Piece(idx, self.hash_piece_list[x:(x+PIECE_HASH_LENGTH-1)]))
    		self.num_of_pieces = self.num_of_pieces + 1
    		
       		x = x+PIECE_HASH_LENGTH
       		idx=idx+1 #increment piece index

       	#sanity check to make sure that is always correct	
       	assert len(self.piece_list) is len(self.hash_piece_list)/PIECE_HASH_LENGTH , \
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
###############################################################

###############################################################
class Piece:
	#INTERFACE
	#
	#variables:
	#	idx 				-Piece index 
	#	hash 				-20 byte has that corresponds to the data in the piece 
	#	num_blocks  		-number of total blocks in the Piece
	# 	blocks[]			-list of Block objects. This should always be ordered by increasing block offset
	#	downloaded  		-(BOOLEAN) is the entire piece downloaded 
	#	verified			-(BOOLEAN) has the piece been verified 
	# 	
	#   
	#methods:
	#
	#	__str__ 			-overrides the string method to print the information about the piece
	#	init_blocks()		-creates initial block objects and puts them into the blocks[] list
	#	verify_piece		-checks the piece against the hash. if all blocks have been downloaded 
	#							properly it will return True. once set, it will always return true
	#	extract_data		-compiles all the block data into a single string and returns 


	def __init__(self,idx, hash):
		self.idx = idx	#
		self.hash = hash
		self.downloaded = False #indicates if all the data for the Piece has been downloaded
		self.verified = False 	#indicates if the Piece has been successfully verified with hash
		self.loaded = False		#indicates if piece is currently loaded in mem

		self.num_blocks = int(math.ceil(float()))

		self.blocks = []
		self.init_blocks()


	def __str__(self):
		#prints out the piece. <idx>: <hash> 
		out = 'Piece idx: ' + str(self.idx) + ' Hash: ' + str(self.hash) + ' DL: ' + str(self.downloaded) \
		+ ' Ver: ' + str(self.verified)
		return out

	

	# Methods
	def init_blocks(self):
		pass

	def extract_data(self):
		#extracts data from all the blocks and returns a concatenated string of the piece
		#	if it has not been verified it will return an empty string '' instead
		data = []
		if self.verified:
			for block in self.blocks:
				data.extend(block.data)

			return ''.join(data)
		else:
			return ''

	def verify_piece(self):
		#attempts to verify the piece against its hash value. returns boolean of result
		#will also set the verified to 1 

		#check if it is even all here
		if not self.downloaded:
			return False
		#check against SHA1 hash. TODO
		hash_of_data = Decoder.create_hash(self.data)

		if hash_of_data == self.hash:
			self.verified = True
			print self
			return True
		else:
			return False
###############################################################

###############################################################
class Block:
	#INTERFACE
	#
	# variables:
	#	size 				-Size in bytes of the block
	#	offset_idx			-block offset index. This is the offset in the piece data
	#	data 				-actual file data! this will be a string 
	#	downloaded 			-(BOOLEAN) is the block downloaded	
	def __init__(self,offset_idx,size):
		self.size = size
		self.offset_idx = offset_idx

		self.data = []
		self.downloaded = 0
###############################################################



###testing 
if __name__ == '__main__':
	pm = PieceManager('',16384, \
		"Itshouldbetwentybit_Itshouldbetwentybit_Itshouldbetwentybit_Itshouldbetwentybit_", 4)


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