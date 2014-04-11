class PieceManager:
    # Attributes

    # Constructors
    def __init__(self, piece_length):

        # Populating some attributes (nothing to see here)
        self.piece_length = piece_length
        self.downloaded = 0
        self.uploaded = 0
        self.corrupt = 0

        self.TrackM1 = ''
        self.PeerM1 = ''


    # Methods
