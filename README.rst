####
RIPWHINE - an easy-to-use single purpose ripper and encoder
####

Requires ``musicbrainzngs``

Not configurable, you can set the destination dir in the UI.

Originally a one-day hack job, but I guess it keeps improving slowly

Usage
-----

$ python setup.py install

Launch with ``./ripwhine``

The menu is pretty self-evident, and works without
pressing enter between commands.

Feel free to experiment with it, it can't break anything!

Output
------

There's a format to how ripped files are stored, based on
my view (that I was told about as a kid) that CDs are organized
by artists alphabetically and discs by year.

The output is a directory for the artist, and sub-directories
for discs named "Year - Album Name."

The year might be a bit tricky when using the shell to play music so a
symlink is set up for the album as well.

Next to the flacs is a file ``musicbrainz.id`` with the disc id
used for identification.

Apps like Rhythmbox probably don't care, or might read
the files in twice, or whatever. Can't say I'm affected
by that because I use mplayer ;)

cdparanoia runs with -X so it aborts on fatal errors.

lame runs with --best because it seems reasonable.

Quickstart
----------

* Insert CD
* i for identify
* r for rip

Exchange a new CD in and GOTO 10

TODO/Wishlist
-------------

Would be nice if:

* we were tied to the optical drive's events to automatically identify discs
* better output from cdparanoia and flac

An original vision was that ripwhine would create a list
of your music. That didn't make it during the day and should
be easy enough to implement later using os.path.walk() or
a separate software, because of the id files.

Greets
------

I'm quite sure it was sph who told me about organizing discs.

Props to part for pointing me at musicbrainz to replace freedb.

Contact
-------

Email me at mjt@fadconsulting.com or whatever.

License
-------

    Everyone is permitted to fork and modify and redistribute the code
    as long as the original author's name is visible somewhere.

If you got good ideas, push them back plz.

