import os.path
import bencode
import hashlib


#--------------Encoders/Decoders---------------

# Used to decode the whole torrent file
def bdecode_torrent(file):
    # Check if the file is a valid file
    if (os.path.isfile(file) is False):
        print "Invalid Torrent File"
        exit()
    else:
    # Valid file, open it and read the line
        fh1 = open(file, 'rb')
        encoded_data = fh1.read()
        fh1.close()

        decoded_data = bencode.bdecode(encoded_data)
        return decoded_data


# Used to encode data, mainly for encoding info dictionary
def bencode_data(data):
    # encode the info dictionary, this is used for SHA1
    encoded_data = bencode.bencode(data)
    return encoded_data


# Used to decode data, mainly for decoding tracker response
def bdecode_data(data):
    decoded_data = bencode.bdecode(data)
    return decoded_data


# Used to change escaped binary to url encoded
def pencode_data(data):
    encoded_data = ''.join(map(lambda c: '%%%02x' % c, map(ord, data)))
    return encoded_data

#-------------------Hashes------------------------


# This creates a SHA1 hash of the data
def create_hash(data):
    info_hash = hashlib.sha1(data).digest()
    return info_hash

#------------------Printing Data------------------


# Use this if you want to print escaped binary strings
# Setting all to True will print no ASCII equivalent characters
# Setting all to False will print ASCII characters
def print_escaped_hex(output_string, all):
    if all is True:
        print ''.join(map(lambda c: '\\x%02x' % c, map(ord, output_string)))
    else:
        print repr(output_string)


def print_hex(output_string):
    print ''.join(map(lambda c: '%02x' % c, map(ord, output_string)))


# Use this if you want to print escaped binary strings (\x00)
# as url encoded strings (%00)
def print_url_hex(output_string, all):
    if all is True:
        print ''.join(map(lambda c: '%%%02x' % c, map(ord, output_string)))
    else:
        print repr(output_string).replace('\\x', '%')
