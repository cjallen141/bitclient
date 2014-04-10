import os.path
import bencode


def decode_torrent(file):
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


def encode_info(data):
    # encode the info dictionary, this is used for SHA1
    encoded_data = bencode.bencode(data)
    return encoded_data


def decode_info(data):
    decoded_data = bencode.bdecode(data)
    return decoded_data


def print_hash(hash_out):
    print ''.join(map(lambda c: '\\x%02x' % c, map(ord, hash_out)))
