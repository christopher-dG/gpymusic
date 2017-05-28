from . import common

from time import sleep

import curses as crs
import sys


class Writer():

    def __init__(
            self, main, inbar, infobar, outbar,
            curses=True, colour=False, test=False):
        """
        Writer constructor.

        Arguments:
        main/inbar/infobar/outbar: curses windows.

        Keyword arguments:
        curses=True: Flag for disabling curses output.
        colour=False: Flag for disabling colour output.
        test=False: Flag to disable all output for unit testing.
          If test is True, then curses must be disabled.
        """
        if test and curses:
            print('Incompatible arguments to writer: '
                  'curses must be disabled to test.')
            sleep(1)
            sys.exit()

        self.main = main
        self.inbar = inbar
        self.infobar = infobar
        self.outbar = outbar
        self.curses = curses
        self.colour = colour
        self.test = test
        self.xlimit = self.main.getmaxyx()[1] if main is not None else 0
        self.ylimit = self.main.getmaxyx()[0] if main is not None else 0

    @staticmethod
    def trunc(string, ch):
        """
        Pads a string with '...' if it is too long to fit in a window.

        Arguments:
        string: String to be truncated.
        ch: Max length for the string.

        Returns: The original string if it is short enough to be displayed,
          otherwise the string truncated and padded with '...'.
        """

        if ch < 0 or len(string) <= ch:
            return string
        else:
            return string[:-((len(string) - ch) + 3)] + '...'

    def replace_windows(self, main, inbar, infobar, outbar):
        self.main = main
        self.inbar = inbar
        self.infobar = infobar
        self.outbar = outbar
        self.ylimit = self.main.getmaxyx()[0]
        self.xlimit = self.main.getmaxyx()[1]

    def addstr(self, win, string):
        """
        Replace the contents of a window with a new string.
          Not for anything where position matters.

        Arguments:
        win: Window on which to display the string.
        string: String to be displayed.
        """
        if not self.curses:
            if not self.test:
                print(string)
            return

        win.erase()
        win.addstr(Writer.trunc(string, self.xlimit - 1))
        win.refresh()

    def refresh(self):
        """Refresh all windows."""
        if not self.curses:
            return

        self.main.refresh()
        self.inbar.refresh()
        self.infobar.refresh()
        self.outbar.refresh()

    def now_playing(self, string=None):
        """
        Show 'now playing' information. If both kwargs are None,
          nothing is playing.

        Keyword arguments:
        string=None: Formatted song string.
        """
        if self.test:
            return
        self.addstr(self.infobar, 'Now playing: %s' %
                    (string if string is not None else 'None'))

    def erase_outbar(self):
        """Erases content on the outbar."""
        if not self.curses:
            return

        self.outbar.erase()
        self.outbar.refresh()

    def error_msg(self, msg):
        """
        Displays an error message.

        Arguments:
        win: Window on which to display the message.
        msg: Message to be displayed.
        """
        if self.test:
            return

        self.addstr(
            self.outbar, 'Error: %s. Enter \'h\' or \'help\' for help.' % msg)

    def welcome(self):
        """Displays a welcome message."""
        if not self.curses:
            if not self.test:
                print('Welcome to Google Py Music!')
            return

        try:
            self.main.addstr(
                5, int(crs.COLS / 2) - 13, 'Welcome to Google Py Music!'
            )
            self.main.refresh()
        except:  # If this errors for some reason, just don't display anything.
            pass

    def goodbye(self, msg):
        """
        Exit gpymusic.

        Arguements:
        msg: Message to display prior to exiting.
        """
        if not self.curses:
            if not self.test:
                print(msg)
            sys.exit()

        self.addstr(self.outbar, msg)
        common.mc.logout()
        try:
            common.client.mm.logout()
        except:
            pass
        sleep(2)
        crs.curs_set(1)
        crs.endwin()
        sys.exit()

    def get_input(self):
        """
        Get user input in the bottom bar.

        Returns: The user - inputted string.
        """
        if not self.curses:
            return input('Enter some input: ')

        self.addstr(self.inbar, '> ')
        crs.curs_set(2)  # Show the cursor.

        try:
            string = self.inbar.getstr()
        except KeyboardInterrupt:
            self.goodbye('Goodbye, thanks for using Google Py Music!')

        self.inbar.deleteln()
        crs.curs_set(0)  # Hide the cursor.

        return string.decode('utf-8')

    def outbar_msg(self, msg):
        """
        Display a basic output message.

        Arguments:
        msg: Message to be displayed.
        """
        if self.test:
            return
        self.addstr(self.outbar, msg)

    def measure_fields(self, width):
        """
        Determine max number of  characters and starting point
          for category fields.

        Arguments:
        width: Width of the window being divided.

        Returns: A tuple containing character allocations
          and start positions.
        """
        padding = 1  # Space between fields.
        i_ch = 3  # Characters to allocate for index.
        # Width of each name, artist, and album fields.
        n_ch = ar_ch = al_ch = int((width - i_ch - 3 * padding) / 3)
        al_ch -= 1  # Hacky guard against overflow.

        total = sum([i_ch, n_ch, ar_ch, al_ch, 3 * padding])

        if total != width:  # Allocate any leftover space to name.
            n_ch += width - total

        # Field starting x positions.
        n_start = 0 + i_ch + padding
        ar_start = n_start + n_ch + padding
        al_start = ar_start + ar_ch + padding

        return (i_ch, n_ch, ar_ch, al_ch,
                n_start, ar_start, al_start)

    def display(self):
        """Update the main window with some content."""
        if common.v.is_empty():
            return

        c = common.v  # Content to display.

        if not self.curses:
            if not self.test:
                i = 1
                if 'songs' in c and c['songs']:
                    print('Songs:')
                for song in c['songs']:
                    print('%d: %s' % (i, str(song)))
                    i += 1
                if 'artists' in c and c['artists']:
                    print('Artists:')
                for artist in c['artists']:
                    print('%d: %s' % (i, str(artist)))
                    i += 1
                if 'albums' in c and c['albums']:
                    print('Albums:')
                for album in c['albums']:
                    print('%d: %s' % (i, str(album)))
                    i += 1
            return

        cl = self.colour
        self.main.erase()
        y, i = 0, 1  # y coordinate in main window, current item index.
        (i_ch, n_ch, ar_ch, al_ch, n_start,
         ar_start, al_start) = self.measure_fields(self.xlimit)

        # Songs header.
        if 'songs' in c and c['songs']:
            self.main.addstr(
                y, 0, '#', crs.color_pair(2) if cl else crs.A_UNDERLINE)
            self.main.addstr(
                y, n_start, Writer.trunc('Title', n_ch),
                crs.color_pair(2) if cl else crs.A_UNDERLINE)
            self.main.addstr(
                y, ar_start, Writer.trunc('Artist', ar_ch),
                crs.color_pair(2) if cl else crs.A_UNDERLINE)
            self.main.addstr(
                y, al_start, Writer.trunc('Album', al_ch),
                crs.color_pair(2) if cl else crs.A_UNDERLINE)

            y += 1

            # Write each song.
            for song in c['songs']:
                self.main.addstr(
                    y, 0, str(i).zfill(2),
                    crs.color_pair(3 if y % 2 == 0 else 4) if cl else 0)
                self.main.addstr(
                    y, n_start, Writer.trunc(song['name'], n_ch),
                    crs.color_pair(3 if y % 2 == 0 else 4) if cl else 0)
                if song['kind'] == 'song':
                    self.main.addstr(
                        y, ar_start, Writer.trunc(song['artist']['name'], ar_ch),  # noqa
                        crs.color_pair(3 if y % 2 == 0 else 4) if cl else 0)
                    self.main.addstr(
                        y, al_start, Writer.trunc(song['album']['name'], al_ch),  # noqa
                        crs.color_pair(3 if y % 2 == 0 else 4) if cl else 0)
                else:
                    self.main.addstr(
                        y, ar_start, Writer.trunc(song['artist'], ar_ch),
                        crs.color_pair(3 if y % 2 == 0 else 4) if cl else 0)
                    self.main.addstr(
                        y, al_start, Writer.trunc(song['album'], al_ch),
                        crs.color_pair(3 if y % 2 == 0 else 4) if cl else 0)

                y += 1
                i += 1

        # Artists header.
        if 'artists' in c and c['artists']:
            self.main.addstr(
                y, 0, '#', crs.color_pair(2) if cl else crs.A_UNDERLINE)
            self.main.addstr(
                y, ar_start, Writer.trunc('Artist', n_ch),
                crs.color_pair(2) if cl else crs.A_UNDERLINE)

            y += 1

            # Write each artist.
            for artist in c['artists']:
                self.main.addstr(
                    y, 0, str(i).zfill(2),
                    crs.color_pair(3 if y % 2 == 0 else 4) if cl else 0)
                self.main.addstr(
                    y, n_start, Writer.trunc(artist['name'], n_ch),
                    crs.color_pair(3 if y % 2 == 0 else 4) if cl else 0)

                y += 1
                i += 1

        # Albums header.
        if 'albums' in c and c['albums']:
            self.main.addstr(
                y, 0, '#', crs.color_pair(2) if cl else crs.A_UNDERLINE)
            self.main.addstr(
                y, n_start, Writer.trunc('Album', n_ch),
                crs.color_pair(2) if cl else crs.A_UNDERLINE)
            self.main.addstr(
                y, ar_start, Writer.trunc('Artist', ar_ch),
                crs.color_pair(2) if cl else crs.A_UNDERLINE)

            y += 1

            # Write each album.
            for album in c['albums']:
                self.main.addstr(
                    y, 0, str(i).zfill(2),
                    crs.color_pair(3 if y % 2 == 0 else 4) if cl else 0)
                self.main.addstr(
                    y, n_start, Writer.trunc(album['name'], n_ch),
                    crs.color_pair(3 if y % 2 == 0 else 4) if cl else 0)
                self.main.addstr(
                    y, ar_start, Writer.trunc(album['artist']['name'], ar_ch),  # noqa
                    crs.color_pair(3 if y % 2 == 0 else 4) if cl else 0)

                y += 1
                i += 1

        self.main.refresh()
