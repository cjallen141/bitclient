from Queue import Queue
import Decoder
import sys
import os
from bitstring import BitArray
import math
import struct

testing = True

PIECE_HASH_LENGTH = 20  # number of bytes per piece in the hash list
#BLOCK_SIZE = 2**14
BLOCK_SIZE = 2 ** 14  # size in bytes of a block
#


class PieceManager:
    # INTERFACE
    #
    # variables:
    #
    #   desired_piece_q     -Queue that holds all the currently desired pieces
    #   downloaded_piece_q  -Queue to PUT downloaded pieces after completed download of pieces
    #   num_of_pieces       - total number of pieces
    #   f                   -file to write data to
    #
    # methods:
    #
    #   is_finished_downloading() -checks if the file has been completely downloaded
    #
    #   print_progress()        -prints the current downloaded piece list with missing spaces for
    #                               pieces not downloaded
    # Constructors

    def __init__(self, data):

        #total number of bytes in a piece
        self.piece_byte_length = data['piece_length']
        #total length of the file in bytes
        self.total_length = data['file_length']
        self.multi_file = data['multi_file']
        self.length = data['length']  # Can be a list
        self.path = data['path']
        self.torent_name = data['name']
        self.file_name = data['file_name']  # Can be a list
        self.downloaded = 0
        self.uploaded = 0
        self.corrupt = 0
        self.hash_piece_list = data['pieces_hash']
        self.num_of_pieces = 0
        # used to initially hold all the pieces. during normal mode, this will
        # be empty
        self.piece_list = []

        self.generate_piece_list()
        # self.read_piece_list(self.hash_piece_list)

        # holds all the currently desired pieces.
        self.desired_piece_q = Queue()

        #list of completed downloaded pieces.This should be kept
        self.downloaded_piece_list = []
                                        #     ordered by the piece index
        #queue of downloaded pieces from peers
        self.downloaded_piece_q = Queue()

        self.gen_desired_piece_q()

       # f=open(file_info['file_name'],'a+')
    # Methods
    def is_finished_downloading(self):
        # Go through the downloaded_piece_q and verify
        while not self.downloaded_piece_q.empty():
            cur_piece = self.downloaded_piece_q.get()
            # Testing stuff
            # data = []
            # for block in cur_piece.blocks:
            #     data.extend(block.data)
            # data = ''.join(data)
            # new_hash = Decoder.create_hash(data)
            # Decoder.print_escaped_hex(new_hash, True)
            # Decoder.print_escaped_hex(cur_piece.hash, True)
            # print new_hash == cur_piece.hash

            if not cur_piece.verify():
                if testing:
                    print 'Piece %d Not Verified' % cur_piece.idx
                cur_piece.clean()
                self.desired_piece_q.put(cur_piece)
                return False
            else:
                if testing:
                    print 'Piece %d Verified' % cur_piece.idx

        for piece in self.piece_list:
            if not piece.verified:
                return False

        return True
        # check if the file is completely downloaded

    def generate_piece_list(self):
        # this will parse the piece_list given to it by the tracker manager
        #
        assert (len(self.hash_piece_list) % PIECE_HASH_LENGTH == 0 ), \
            "Check piece list size. Must be equal to piece_byte_length"
        x = 0
        idx = 0
        bytes_remaining = self.total_length
        piece_size = self.piece_byte_length

        while(x < (len(self.hash_piece_list))):
            # iterate over the hash string and extract out the hashes
            # populates the piece_list list with piece objects

            if(bytes_remaining >= self.piece_byte_length):
                piece_size = self.piece_byte_length
            else:
                piece_size = bytes_remaining

            self.piece_list.append(Piece(idx,
                                         self.hash_piece_list[
                                             x:(x + PIECE_HASH_LENGTH)],
                                         piece_size))

            self.num_of_pieces = self.num_of_pieces + 1

            bytes_remaining -= piece_size
            x = x + PIECE_HASH_LENGTH
            idx = idx + 1  # increment piece index

        # sanity check to make sure that is always correct
        assert len(self.piece_list) == len(self.hash_piece_list) / PIECE_HASH_LENGTH , \
            "the piece list doesn't have the correct number of pieces"

        assert bytes_remaining == 0 , \
            "there are bytes left over not put into piece. what gives..."
        assert x == len(self.hash_piece_list)

        assert x == self.num_of_pieces * PIECE_HASH_LENGTH

    def gen_desired_piece_q(self):
        # explicitly removing the piece from self.pieces and putting it into
        # the desired queue
        assert len(self.piece_list) != 0 , \
            "piece list is empty, something went wrong"

        # print 'generating desired piece q..'
        x = 0
        for piece in self.piece_list:

            #piece = self.piece_list.pop(0)
            # print piece
            self.desired_piece_q.put(piece)
        # return self.desired_piece_q

    # This determines whether we should be intersted in the peer
    def is_interested(self, peer_bitfield):
        # Go through the bitfield
        print peer_bitfield.bin
        for i in range(0, len(peer_bitfield)):
            if (peer_bitfield[i] and not self.piece_list[i].verified):
                return True
        return False

    def get_print_progress(self):
        # print the current progress of the file. This will be helpful for debugging and using the
        # program visually
            count = 0
            for piece in self.piece_list:
                if piece.verified:
                    count += 1

            out = []
            out.append('Progress: ')
            out.append(str(count))
            out.append(': ')

            done = (float(count) / self.num_of_pieces)
            blocks_done = int(done * 20)
            out.extend(['='] * blocks_done)
            out.extend('>')
            out.extend([' '] * (20 - blocks_done - 1))
            out.extend(': (')
            percent_done = done * 100
            out.extend(str(percent_done) + ')')
            # for i in x:
            #    out.append('=')
            # out.append('>')
            # out.append(str(math.ceil(float(count)/self.num_of_pieces)))
            # out.append('%')

            out.append('\r')
            return ''.join(out)
            # sys.stdout.write("".join(out))
            # sys.stdout.flush()
            # may want to move the actual printing to another function if want to format a bunch together
            # the output looks like this: 'Downloaded Pieces: |_|_|_|#|#|....'
            # where the #'s are downloaded

    def write_out_to_file(self):
        # 4/21: ONLY CALL THIS WHEN COMPLETELY READY TO WRITE OUT THE FILE!
        print 'got here'

        if self.multi_file:
            # Put all the data into one big variable
            piece_start = 0
            out = ''

            for i in range(0, len(self.file_name)):
                p = self.path + os.sep + ''.join(self.file_name[i][0])

                if not os.path.exists(os.path.dirname(p)):
                    os.makedirs(os.path.dirname(p))

                with open(p, 'w') as file_obj:
                    length = self.length[i]

                    for j in range(piece_start, len(self.piece_list)):
                        out = out.join(self.piece_list[j].extract_data())
                        if out > self.length[i]:
                            piece_start = j
                            break

                    file_obj.write(out[:length])
                    out = out[length:]
        else:
            p = self.path + ''.join(self.file_name)
            with open(p, 'w') as file_obj:
                for piece in self.piece_list:
                    out = piece.extract_data()
                    file_obj.write(out)


        print 'finished'


class Piece:
    # INTERFACE
    # Piece(idx, hashed_val, piece_size)
    #
    # variables:
    #   idx                 -Piece index
    #   hash                -20 byte has that corresponds to the data in the piece
    #   num_blocks          -number of total blocks in the Piece
    #   blocks[]            -list of Block objects. This should always be ordered by increasing block offset
    #   downloaded          -(BOOLEAN) is the entire piece downloaded
    #   verified            -(BOOLEAN) has the piece been verified
    #   psize               -size of the piece in bytes
    #
    #
    # methods:
    #
    #   __str__             -overrides the string method to print the information about the piece
    #   init_blocks()       -creates initial block objects and puts them into the blocks[] list
    #   is_downloaded()     -checks if all the blocks in the piece have been downloaded
    #   verify_piece()      -checks the piece against the hash. if all blocks have been downloaded
    #                           properly it will return True. once set, it will always return true
    #                           NOTE: THIS SHOULD ONLY BE CALLED BY THE PIECEMANAGER BECAUSE IT WILL SAY FALSE FOR PARTIALLY DOWNLOADED
    # BEWARE!!@#!@#
    #   extract_data()      -compiles all the block data into a single string and returns
    # clean()             -resets the Piece. Clears all data from the blocks
    # and sets all state to undownloaded and unverified

    def __init__(self, idx, hashed_val, piece_size):
        self.idx = idx  #
        self.hash = hashed_val
        self.psize = piece_size
        #indicates if all the data for the Piece has been downloaded
        self.downloaded = False
        #indicates if the Piece has been successfully verified with hash
        self.verified = False
        self.loaded = False  # indicates if piece is currently loaded in mem
        # determine how many blocks go in the piece
        self.num_blocks = int(math.ceil(float(self.psize) / BLOCK_SIZE))

        self.blocks = []
        self.init_blocks()

    def __str__(self):
        # prints out the piece. <idx>: <hash>
        out = 'Piece idx: ' + str(self.idx) + ' Hash: ' + str(self.hash) + ' DL: ' + str(self.downloaded) \
            + ' Ver: ' + str(self.verified) + ' Size: ' + str(self.psize)
        return out

    # Methods
    def init_blocks(self):
        x = 0
        block_size = BLOCK_SIZE
        bytes_remaining = self.psize
        block_offset = 0
        while(x < self.num_blocks):
            if(bytes_remaining >= BLOCK_SIZE):
                block_size = BLOCK_SIZE
            else:
                block_size = bytes_remaining

            self.blocks.append(Block(x, block_offset, block_size))

            x += 1
            bytes_remaining -= block_size
            block_offset += block_size

    def extract_data(self):
        # returns current data in all the blocks. if a block isn't downloaded,
        # this will be kinda garbage
        data = []
        for block in self.blocks:
            data.extend(block.data)
        return ''.join(data)

    def is_downloaded(self):
        # check if all the blocks in the piece have been downloaded
        ans = True
        for block in self.blocks:
            if block.downloaded == False:
                ans = False
        self.downloaded = ans
        return ans

    def verify(self):

        # attempts to verify the piece against
        # its hash value. returns boolean of result
        # will also set the verified to 1
        # check all the blocks if they have been
        # downloaded. Once they are all downloaded

        if not self.downloaded:
            self.verified = False
            return False

        # check against SHA1 hash.
        hash_of_data = Decoder.create_hash(self.extract_data())
        #Decoder.print_escaped_hex(hash_of_data, True)
        #Decoder.print_escaped_hex(self.hash, True)
        # print "checking piece, data: " + str(self.extract_data())
        # print "size: " + str(len(self.extract_data()))
        # print "hash : " + str(hash_of_data)
        # print "hash in list: " + str(self.hash)
        if hash_of_data == self.hash:
            self.verified = True
            return True
        else:
            self.verified = False
            return False

    def clean(self):
        # this is used to clearout a piece . basically resets it if the data is
        # bad
        for block in self.blocks:
            block.data = ''
            block.downloaded = False
        self.downloaded = False
        self.verified = False

#

#


class Block:
    # INTERFACE
    #
    # variables
    #   block_size              -Size in bytes of the block
    #   offset_idx          -block offset index. This is the offset in the piece data
    #   data                -actual file data! this will be a string
    #   downloaded          -(BOOLEAN) is the block downloaded

    def __init__(self, idx, offset_idx, size):
        self.idx = idx
        self.block_size = size
        self.offset_idx = offset_idx

        self.data = ''
        self.downloaded = False

    def __str__(self):
        out = 'Block idx: ' + str(self.idx) + ' Offset idx: ' + str(self.offset_idx) + ' Size: ' + str(self.block_size) \
            + ' Downloaded: ' + str(self.downloaded)
        return out

#


# testing############################################
if __name__ == '__main__':
    # testing#
    # file will be 155 bytes long. Each piece will hold 10 bytes. Each block will be 2 bytes long.
    # intentionally making it not even divisible

    # generate file
    file_name = 'datapath.png'
    f = open("../../datapath.png")
    file_content = f.read()
    #file_content = 'thisisten_thisisten_thisisten_thisisten_thisisten_thisisten_thisisten_thisisten_thisisten_thisisten_thisisten_thisisten_thisisten_thisisten_thisisten_five0'
    print 'file length (bytes): ' + str(len(file_content))
    file_length = len(file_content)
    pSize = 100
    BlOCK_SIZE = 4
    # create file data
    file_data = {}
    file_data['multi_file'] = False
    file_data['file_name'] = file_name
    file_data['length'] = len(file_content)
    file_data['piece_length'] = pSize

    # create the hash_list
    hash_list = []
    x = 0
    while(x < file_length):
        hash_list.extend(Decoder.create_hash(file_content[x:x + pSize]))

        x = x + pSize
    hash_list = ''.join(hash_list)
    file_data['pieces_hash'] = hash_list
    #

    num_of_pieces = int(math.ceil(float(file_length) / pSize))
    print 'Number of pieces: ' + str(num_of_pieces)

    print 'length of hash_list (length*pSize): ' + str(len(hash_list))

    # now start up the PieceManager
    pm = PieceManager(file_data)
    print "starting Piecemanager...."

    # checking generate_piece_list
    # print "checking Piece list:"
    # print "\tnumber of pieces in piece list: " + str(len(pm.piece_list))
    # for piece in pm.piece_list:
    #    print str(piece)
    #    for block in piece.blocks:
    #        print "\t" + str(block)

    # check generate desired piece q
    pm.gen_desired_piece_q()

    assert (pm.is_finished_downloading() == False)

    # simulate downloading all the blocks
    index_into_file = 0
    for piece in pm.piece_list:
        for block in piece.blocks:
            block.downloaded = True
            block.data = file_content[
                index_into_file:index_into_file + block.block_size]
            index_into_file += block.block_size
        # check the piece if downloaded
        piece.is_downloaded()
        pm.downloaded_piece_q.put(piece)

    #
    # check if downloaded
    a = pm.is_finished_downloading()

    for piece in pm.piece_list:
        print piece

    print "\n\n"
    pm.is_finished_downloading()
    for piece in pm.piece_list:
        print piece
    print "all downloaded!"

    # test writing out to file
    pm.write_out_to_file()
