#! /usr/bin/env python3

from gmusicapi import Musicmanager

mm = Musicmanager()
mm.perform_oauth()
if mm.login():
    print('Authorization successful.')
    mm.logout()
else:
    print('Authorization failed.')
