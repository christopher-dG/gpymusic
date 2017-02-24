class View(dict):
    """A View contains the content displayed in the main window."""

    def __init__(self, d):
        for k in d:
            self.__setitem__(k, d[k])
