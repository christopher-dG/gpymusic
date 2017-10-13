class _Provider:
    """
    Provider is the base class for music providers.
    All required methods are specified here.
    """
    def __init__(self):
        raise NotImplementedError

    def search(query, limit=None):
        raise NotImplementedError

    def play(item):
        raise NotImplementedError

from .local import Local  # noqa
from .google import Google  # noqa
from .spotify import Spotify  # noqa
