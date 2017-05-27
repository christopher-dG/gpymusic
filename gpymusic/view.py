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
            if isinstance(d, dict):
                for k in d:
                    self[k] = d[k]
            else:
                raise TypeError('Initializing View with invalid argument')

    def __setitem__(self, key, val):
        """Restrict values to lists only."""
        if not isinstance(val, list):
            raise TypeError('View can only hold lists as values.')
        super().__setitem__(key, val)

    def __len__(self):
        """Return the sum of each list's length."""
        return sum(len(self[k]) for k in self)

    def replace(self, other):
        """Replace the view's contents with some other dict."""
        self = self.__init__(other)

    def clear(self):
        """Clear elements without removing keys."""
        for k in self.keys():
            del self[k][:]

    def is_empty(self):
        """Returns whether or not the view is empty."""
        return all(not self[k] for k in self)

    def copy(self):
        """Return a deep copy of the view's contents."""
        return {k: self[k][:] for k in self}
