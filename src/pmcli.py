#!/usr/bin/env python3

import consts
import json
import library
import start
import view
from os.path import exists, isfile, join
from random import shuffle
from warnings import filterwarnings


def transition(input):
    """
    Route input to the appropriate function.

    Arguments:
    input: User input.
    """
    commands = {  # Command -> function mapping.
        'h': help,
        'help': help,
        'e': expand,
        'expand': expand,
        's': search if consts.mc.is_subscribed else consts.l.search,
        'search': search if consts.mc.is_subscribed else consts.l.search,
        'p': play if consts.mc.is_subscribed else consts.l.play,
        'play': play if consts.mc.is_subscribed else consts.l.play,
        'q': queue,
        'queue': queue,
        'w': write,
        'write': write,
        'r': restore,
        'restore': restore,
    }

    arg = None
    if consts.v is None:
        consts.w.now_playing()

    try:
        command, arg = input.split(maxsplit=1)
    except ValueError:  # No argument.
        command = input

    if command in commands:
        commands[command](arg)
        if consts.v is not None and consts.w.curses:
            consts.w.display()
    else:
        consts.w.error_msg('Nonexistent command')


def get_option(num, limit=-1):
    """
    Select a numbered MusicObject from the main windoconsts.w.

    Arguments:
    num: Index of the MusicObject in the main window to be returned.

    Keyword argumnents:
    limit=-1: Number of songs to generate for artists,
      determined by terminal height.

    Returns: The MusicObject at index 'num'.
    """
    total = sum(len(consts.v[k]) for k in consts.v.keys())
    if num < 0 or num > total:
        p
        consts.w.error_msg('Index out of range: valid between 1-%d' % total)
        return None

    i = 1
    for key in ('songs', 'artists', 'albums'):  # Hardcoded to guarantee order.
        for item in consts.v[key]:
            if i == num:
                # Always return item with all content.
                item.fill(consts.mapping[item['kind'] + 's']['lookup'], limit)
                return item
            else:
                i += 1


def queue(arg=None):
    """
    Display the current queue, or add an item to the queue.

    Keyword arguments:
    arg=None: Index of the MusicObject in the main window to add to
      the queue, 'c' to clear the queue, None to display the queue, or
      a space - delimited list of indices to add to the queue, i.e. '1 2 3'.
    """
    if arg is None:
        if not consts.q:  # Nothing to display.
            consts.w.error_msg('The queue is empty')

        else:  # Display the queue.
            if consts.w.curses:
                # Allow room for header.
                limit = consts.w.main.getmaxyx()[0] - 2
            else:
                limit = -1
            if consts.q:
                consts.v = view.View(consts.q.collect(limit))
            else:
                consts.w.error_msg('Wrong context for queue')

    else:
        if arg is 'c':  # Clear the queue.
            consts.w.outbar_msg('Cleared queue.')
            del consts.q[:]

        else:
            try:
                num = int(arg)

            except ValueError:
                try:  # Check for multi-option argument.
                    nums = [int(i) for i in arg.split()]
                except ValueError:  # Invalid argument.
                    consts.w.error_msg('Invalid argument to queue')
                else:  # Add all arguments to the queue.
                    consts.w.outbar_msg('Adding items to the queue...')
                    items = [get_option(num) for num in nums]
                    count = consts.q.extend(
                        [item for item in items if item is not None])
                    consts.w.outbar_msg('Added %d song%s to the queue.' %
                                        (count, '' if count == 1 else 's'))

            else:
                if (num > len(consts.v['songs']) and  # I love PEP 8.
                        num <= len(consts.v['songs'])
                        + len(consts.v['artists'])):
                    consts.w.error_msg(
                        'Can only add songs or albums to the queue.')
                else:
                    item = get_option(num)
                    if item is not None:
                        count = consts.q.append(item)
                        # I feel so dirty using double quotes.
                        consts.w.outbar_msg("Added %d song%s to the queue." %
                                            (count, '' if count == 1 else 's'))


def expand(num=None):
    """
    Display all of a MusicObject's information: songs, artists, and albums.

    Keyword arguments:
    num=None: Index of the MusicObject in the main window to be expanded.
    """
    if not consts.mc.is_subscribed:
        consts.w.error_msg('Free users cannot expand songs.')
    if num is None:  # No argument.
        consts.w.error_msg('Missing argument to play')
    elif consts.v is None:  # Nothing to expand.
        consts.w.error_msg('Wrong context for expand.')
    else:
        try:
            num = int(num)
        except ValueError:  # num needs to be an int.
            consts.w.error_msg('Invalid argument to play')
        else:
            if not consts.w.curses:
                limit = -1
            else:
                # Artists only have one artist and albums only have one album,
                # so we can allocate more space for the other fields.
                limit = int((consts.w.main.getmaxyx()[0] - 9) / 2)
            item = get_option(num, limit)

            if item is not None:  # Valid input.
                consts.v = view.View(item.collect(limit=limit))
                consts.w.erase_outbar()


def help(arg=0):
    """
    Display basic pmcli commands.

    Keyword arguments:
    arg=0: Irrelevant.
    """
    consts.v = None
    if not consts.w.curses:
        return

    # Don't use generic addstr() because we don't want to call trunc() here.
    consts.w.main.erase()
    consts.w.main.addstr(
        """
        Commands:
        s/search searchterm: Search for searchterm
        e/expand 123: Expand item number 123
        p/play: Play current queue
        p/play s: Shuffle and play current queue
        p/play 123: Play item number 123
        q/queue: Show current queue
        q/queue 123:  Add item number 123 to queue
        q/queue 1 2 3:  Add items 1, 2, 3 to queue
        q/queue c:  Clear the current queuen
        w/write filename: Write current queue to filename
        r/restore filename: Replace current queue with playlist from filename
        h/help: Show this help message
        Ctrl-C: Exit pmcli
        """
    )
    consts.w.main.refresh()


def play(arg=None):
    """
    Play a MusicObject or the current queue.

    Keyword arguments:
    arg=None: A number n to play item n, 's' to play the queue in shuffle mode,
      or None to play the current queue in order.
    """
    if arg is None or arg is 's':
        if not consts.q:  # Can't play an empty queue.
            consts.w.error_msg('The queue is empty')
        else:  # Play the queue.
            if arg is 's':  # Shuffle.
                shuffle(consts.q)
            if consts.w.curses:
                # Allow room for header.
                limit = consts.w.main.getmaxyx()[0] - 1
            else:
                limit = -1
            consts.v = consts.q.collect(limit)
            consts.w.display()
            consts.w.outbar_msg(
                '[spc] pause [q] stop [n] next [9-0] volume [arrows] seek')
            consts.q.play()
            consts.w.erase_outbar()

    elif consts.v is None:  # Nothing to play.
        consts.w.error_msg('Wrong context for play')
    else:
        try:
            num = int(arg)
        except ValueError:  # arg needs to be an int if it isn't 's'.
            consts.w.error_msg('Invalid argument to play')
        else:
            item = get_option(num)

            if item is not None:  # Valid input.
                consts.w.outbar_msg(
                    '[spc] pause [q] stop [n] next [9-0] volume [arrows] seek')
                item.play()
                consts.w.now_playing()
                consts.w.erase_outbar()


def restore(fn=None):
    """
    Restore queue from a file.

    Keyword arguments:
    fn=None: Name of the file containing the playlist.
      File should be at ~ / .local / share / pmcli / playlists / .
    """
    path = join(consts.DATA_DIR, 'playlists')
    if fn is None:  # No argument.
        consts.w.error_msg('Missing argument to restore')
    elif not isfile(join(path, fn)):  # Playlist file doesn't exist.
        consts.w.error_msg('Playlist %s does not exist' % fn)
    else:
        consts.w.outbar_msg('Restoring queue from %s...' % fn)
        try:  # Read the playlist.
            with open(join(path, fn)) as f:
                json_songs = json.load(f)
        except json.decoder.JSONDecodeError:  # Bad file.
            consts.w.error_msg('%s is not a valid playlist file' % fn)
        else:
            consts.q.restore(json_songs)


def search(query=None):
    """
    Search Google Play Music for a given query and update the
      view with the results.

    Keyword arguments:
    query=None: The search query.
    """
    if query is None:  # No argument.
        consts.w.error_msg('Missing search query')
        return

    # Fetch as many results as we can display depending on terminal height.
    if consts.w.curses:
        limit = int((consts.w.main.getmaxyx()[0] - 3) / 3)
    else:
        limit = 50

    consts.w.outbar_msg('Searching for \'%s\'...' % query)
    result = consts.mc.search(query, max_results=limit)
    consts.w.erase_outbar()

    # 'class' => class of MusicObject
    # 'hits' => key in search result
    # 'rslt_key' => per-entry key in search result
    if consts.v is not None:
        consts.v.clear()
    else:
        consts.v = view.View({'songs': [], 'artist': [], 'albums': []})
    iters = {k: iter(result[consts.mapping[k]['hits']])
             for k in consts.v.keys()}
    # Create at most 'limit' of each type.
    for i in range(limit):
        for k in iters.keys():
            try:
                consts.v[k].append(consts.mapping[k]['cls'](
                    next(iters[k])[consts.mapping[k]['rslt_key']]))
            except StopIteration:
                pass
    consts.w.outbar_msg('Search returned %d results.' % len(consts.v))


def write(fn=None):
    """
    Write the current queue to a file.

    Keyword arguments:
    fn=None: File to be written to.
      File is stored at ~ / .local / share / pmcli / playlists / .
    """
    path = join(consts.DATA_DIR, 'playlists')
    if not consts.q:  # Can't save an empty queue.
        consts.w.error_msg('Queue is empty')
    elif fn is None:  # No argument.
        consts.w.error_msg('Missing argument to write')
    elif not exists(path):  # No playlists directory.
        consts.w.error_msg('Path to playlists does not exist')
    elif exists(join(path, fn)):  # Playlist already exists at path/fn.
        consts.w.error_msg('Playist %s already exists' % fn)
    else:  # Write the playlist.
        with open(join(path, fn), 'a') as f:
            json.dump(consts.q, f)
        consts.w.outbar_msg('Wrote queue to %s.' % fn)


filterwarnings('ignore')

if __name__ == '__main__':
    (consts.w.main, consts.w.inbar,
     consts.w.infobar, consts.w.outbar) = start.get_windows()
    consts.w.curses = True
    config = start.read_config()
    colour = start.validate_config(config)
    if colour:
        start.set_colours(config['colour'])
        consts.w.colour = True
    consts.w.welcome()
    start.login(config['user'])
    if not consts.mc.is_subscribed:
        consts.l = library.Library()
    consts.w.addstr(consts.w.infobar,
                    'Enter \'h\' or \'help\' if you need help.')

    while True:
        transition(consts.w.get_input())
