class NowPlaying():
    def __init__(self):
        self.enabled = False

    def initialise(self, filename):
        """
        Initialise the nowplaying file with a filename.

        Arguments:
        filename: The full file path to the nowplaying file.
        """
        self.filename = filename
        self.enabled = True

    def close(self):
        """Overwrite the nowplaying file with an empty file"""
        if not self.enabled:
            return
        f = open(self.filename, 'w')
        f.close()

    def update(self, playing):
        """Overwrite the nowplaying file with a string"""
        if not self.enabled:
            return
        f = open(self.filename, 'w')
        f.write(playing)
        f.close()
