import os.path
import bencode


def decodeTorrent(file):
    # Check if the file is a valid file
    if (os.path.isfile(file) is False):
        print "Invalid Torrent File"
        exit()
    else:
    # Valid file, open it and read the line
        fh1 = open(file, 'rb')
        encodedData = fh1.read()
        fh1.close()

        decodedData = bencode.bdecode(encodedData)
        return decodedData
