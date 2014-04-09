# Bencode Testing
import bencode

fh1 = open('../referenceFiles/WhySoccerMatters-Original.torrent', 'rb');
codedStr = fh1.read();
decodedDict = bencode.bdecode(codedStr)
