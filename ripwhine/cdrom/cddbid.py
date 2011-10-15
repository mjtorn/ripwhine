# vim: tabstop=4 expandtab autoindent shiftwidth=4 fileencoding=utf-8

"""A module containing functions for calculating CDDB disc IDs.

Copyright © 1998 Carey Evans.

     Permission to use, copy, modify, and distribute this software and its
     documentation for any purpose and without fee is hereby granted,
     provided that the above copyright notice appear in all copies and
     that both that copyright notice and this permission notice appear in
     supporting documentation.

The CDDB ID calculating function is described in Ti Kan and Steve
Scherf's cddb.howto.  For more information about the CDDB, see
<URL:http://www.cddb.com/>.  For more information about this software,
see my web page at <URL:http://home.clear.net.nz/pages/c.evans/sw/cd/>
or email me at <c.evans@clear.net.nz>.

Example:

>>> import cddbid
>>> cddbid.discid((150, 20877, 37215, 52545, 71162, 87955, 109837,
...    128030, 146932, 164185, 182460, 199227), 2981)
('b50ba30c', 2981)
>>> cddbid.discid((150, 20877, 37215, 52545, 71162, 87955, 109837,
...    128030, 146932, 164185, 182460, 199227, 223582))
('b50ba30c', 2981)
"""

def _sum(n):
    "Compute the sum of the digits in the decimal `n'."
    ret = 0
    while n > 0:
        ret = ret + (n % 10)
        n = n / 10
    return ret

def msftosec(msf):
    "Convert MSF tuple or frame count to number of seconds."
    try:
        msf[0]
    except:
        return msf / 75
    else:
        return msf[0]*60 + msf[1]

def discid(toc, disclen=None):
    """Compute the CDDB disc ID for a given CD.

    The first parameter `toc' is a sequence of offsets from the CD's
    table of contents.  The second parameter `disclen' is the length
    of the disc in seconds.  Both parameters must be as described in
    the CDDB HOWTO.  If `disclen' is omitted, the last entry in the
    toc is assumed to be the lead-out offset.  If it is given, the
    lead-out offset must not be passed.

    Each offset may either be the number of frames (as recorded in a
    CDDB format file and returned by the `cddb read' command) or a
    tuple containing the number of minutes, seconds and optionally
    frames.  All the following mean the same for a toc entry:

       182460
       (40, 32)
       (40, 32, 60)
    """

    if disclen is None:
        disclen = msftosec(toc[-1])
        toc = toc[:-1]

    n = 0
    for offs in toc:
        n = n + _sum(msftosec(offs))

    t = disclen - msftosec(toc[0])

    return ("%08x" % ((n % 0xff) << 24 | t << 8 | len(toc)), disclen)


# Test the CDDB disc ID generation on the data from my
# "Garbage / Version 2.0" disc.

if __name__ == '__main__':
    toc = (150, 20877, 37215, 52545, 71162, 87955, 109837,
           128030, 146932, 164185, 182460, 199227, 223582)

    print "should be: ('b50ba30c', 2981)"

    id, length = discid(toc)
    print "no length:", (id, length)

    id, length = discid(toc[:-1], length)
    print "w/ length:", (id, length)

# EOF

