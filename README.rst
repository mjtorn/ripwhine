####
RIPWHINE - an easy-to-use single purpose ripper and encoder
####

Requires ``python-musicbrainz2``

Not configurable, you can set the destination dir in the UI.

A one-day hack job.

Usage
-----

$ python setup.py install

Launch with ``./ripwhine``

The menu is pretty self-evident. raw_input and the messaging
don't play well together, so hitting enter will refresh
the state like after [i].

Feel free to experiment with it, it can't break anything!

Quickstart
----------

* Insert CD
* i for identify
* r for rip

Exchange a new CD in and GOTO 10

TODO/Wishlist
-------------

Would be nice if:
* inputting didn't block the messages like it does now
* we were tied to the optical drive's events to automatically identify discs
* better output from cdparanoia and flac
* eject button in the UI

Greets and email
----------------

Props to part for pointing me at musicbrainz to replace freedb.

mjt@fadconsulting.com

License
-------

    Everyone is permitted to fork and modify and redistribute the code
    as long as the original author's name is visible somewhere.

If you got good ideas, push them back to avoid freetard fork hell.


