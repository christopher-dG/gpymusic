class View(dict):
    """A View contains the content displayed in the main window."""

    def __init__(self, d):
        for k in d:
            self[k] = d[k]

    def clear(self):
        """Clear elements without removing keys."""
        for k in self.keys():
            del self[k][:]
