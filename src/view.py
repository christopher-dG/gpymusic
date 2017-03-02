class View(dict):
    """A View contains the content displayed in the main window."""

    def __init__(self, d=None):
        """
        View constructor.

        Keyword arguments:
        d=None: Initial keys and values to initialize the view with.
          Regardless of the value of d, keys 'songs', 'artists' and
          'albums' are created with empty lists as default values.
        """
        self['songs'], self['artists'], self['albums'] = [], [], []
        if d is not None:
            for k in d:
                self[k] = d[k]

    def __setitem__(self, key, val):
        """Restrict values to lists only."""
        if not isinstance(val, list):
            raise TypeError('View can only hold lists as values.')
        super().__setitem__(key, val)

    def __len__(self):
        """
        Get the total number of elements.

        Returns: Sum of each key's length.
        """
        return sum(len(self[k]) for k in self)

    def replace(self, other):
        """Replace the view's contents with some other dict."""
        self = self.__init__(other)

    def clear(self):
        """Clear elements without removing keys."""
        for k in self.keys():
            del self[k][:]
