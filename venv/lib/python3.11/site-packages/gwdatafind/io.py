# Copyright (C) 2022-2025 Cardiff University
#
# This file is part of GWDataFind.
#
# GWDataFind is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GWDataFind is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GWDataFind.  If not, see <https://www.gnu.org/licenses/>.

"""I/O (mainly O) routines for GWDataFind.

The main interface is the `Cache` object, which takes in lists of
URIs and can `~Cache.write` to a number of other formats.

See also :ref:`gwdatafind-htcondor`.
"""

import warnings
from collections import namedtuple
from operator import attrgetter
from os import PathLike
from os.path import dirname
from urllib.parse import urlparse

from igwn_segments import segmentlist

from .utils import filename_metadata

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"


class LalCacheEntry(
    namedtuple("LalCacheEntry", ("obs", "tag", "segment", "url")),
):
    """Simplified version of `lal.utils.CacheEntry`.

    This is provided so that GWDataFind doesn't have to depend on LALSuite.

    Examples
    --------
    >>> LalCacheEntry.from_url("file:///path/to/data/A-MY_DATA-0-100.h5")
    LalCacheEntry(obs='A', tag='MY_DATA', segment=segment(0, 100), url='file:///path/to/data/A-MY_DATA-0-100.h5')
    """

    def __str__(self):
        """Return a `str` representation of this `LalCacheEntry`."""
        seg = self.segment
        return " ".join(map(str, (
            self.obs,
            self.tag,
            seg[0],
            abs(seg),
            self.url,
        )))

    @classmethod
    def from_url(cls, url, **kwargs):
        """Create a new `LalCacheEntry` from a URL following `LIGO-T010150`_.

        .. _LIGO-T010150: https://dcc.ligo.org/LIGO-T010150
        """
        obs, tag, seg = filename_metadata(url)
        return cls(obs, tag, seg, url)


class OmegaCacheEntry(namedtuple(
    "OmegaCacheEntry",
    ("obs", "tag", "segment", "duration", "url")
)):
    """CacheEntry for an omega-style cache.

    Omega-style cache files contain one entry per contiguous directory of
    the form:

        <obs> <tag> <dir-start> <dir-end> <file-duration> <directory>
    """

    def __str__(self):
        """Return a `str` representation of this `OmegaCacheEntry`."""
        return " ".join(map(str, (
            self.obs,
            self.tag,
            self.segment[0],
            self.segment[1],
            self.duration,
            self.url,
        )))


def _omega_cache(cache):
    """Convert a list of `LalCacheEntry` into a list of `OmegaCacheEntry`.

    Returns
    -------
    cache : `list` of `OmegaCacheEntry`
    """
    warnings.warn(
        "The omega cache format is deprecated and will be removed in a future release.",
        DeprecationWarning,
        stacklevel=2,
    )
    wcache = []
    append = wcache.append
    wentry = None
    for entry in sorted(
        cache,
        key=attrgetter("obs", "tag", "segment"),
    ):
        dir_ = dirname(entry.url)

        # if this file has the same attributes, goes into the same directory,
        # has the same duration, and overlaps with or is contiguous with
        # the last file, just add its segment to the last one:
        if wcache and (
                entry.obs == wentry.obs
                and entry.tag == wentry.tag
                and dir_ == wentry.url
                and abs(entry.segment) == wentry.duration
                and (entry.segment.connects(wentry.segment)
                     or entry.segment.intersects(wentry.segment))
        ):
            wcache[-1] = wentry = OmegaCacheEntry(
                wentry.obs,
                wentry.tag,
                wentry.segment | entry.segment,
                wentry.duration,
                wentry.url,
            )
            continue

        # otherwise create a new entry in the omega wcache
        wentry = OmegaCacheEntry(
            entry.obs,
            entry.tag,
            entry.segment,
            abs(entry.segment),
            dir_,
        )
        append(wentry)
    return wcache


class Cache(list):
    """Formatted list of URIs.

    Parameters
    ----------
    items : `list` of `str`
        A list of URIs (`str`).

    Returns
    -------
    cache : `Cache`
        A new `Cache` where each element is a `LalCacheEntry` representing
        a data source URI.
    """

    def __init__(self, items):
        """Initialise a new `Cache`."""
        super().__init__(map(LalCacheEntry.from_url, items))

    @property
    def segments(self):
        """The `igwn_segments.segmentlist` of data covered by this cache."""
        return segmentlist(e.segment for e in self).coalesce()

    @property
    def urls(self):
        """The list of URIs in this `Cache`."""
        return [e.url for e in self]

    @property
    def names(self):
        """The list of URI names (full path without URI scheme or host)."""
        return [urlparse(e.url).path for e in self]

    @property
    def basenames(self):
        """The list of URI base names (file name component only)."""
        return [e.url.rsplit("/", 1)[-1] for e in self]

    def _format_cache(self, fmt):
        """Return a formatted view of this `Cache`."""
        if fmt == "lal":
            return list(self)

        if fmt == "urls":
            return self.urls

        if fmt == "names":
            return self.names

        if fmt == "basenames":
            return self.basenames

        if fmt == "omega":
            return _omega_cache(self)

        msg = f"invalid format '{fmt}'"
        raise ValueError(msg)

    def write(self, output, format="lal"):
        """Write this `Cache` in the given ``format``.

        Parameters
        ----------
        output : `str`, `pathlib.Path`, `file`
            The target filename or path, or an open IO stream to write to.

        format : `str`, optional
            The desired format of the cache file.
            Choose one of

            ``"lal"``
                The LIGO Algorithm Library format, with one
                line per file in the format:

                .. code-block:: text

                    <obs> <tag> <GPS-start> <duration> <url>

            ``"omega"``
                The Omega pipeline format, with one line per
                contiguous directory in the format

                .. code-block:: text

                    <obs> <tag> <dir-start> <dir-end> <file-duration> <directory>

            ``"urls"``
                A list of URLS, one per line.

            ``"names"``
                A list of paths (without a URL scheme), one per line.

            ``"basenames"``
                A list of file basenames (without any paths), one per line.

        Examples
        --------
        >>> urls = find_urls(
        ...     "L",
        ...     "L1_GWOSC_O2_4KHZ_R1",
        ...     1187008880,
        ...     1187008884,
        ...     host="datafind.gwosc.org",
        ...     urltype="osdf",
        ... )
        >>> cache = Cache(urls)
        >>> cache.write(sys.stdout)
        L L1_GWOSC_O2_4KHZ_R1 1187008512 4096 osdf:///gwdata/O2/strain.4k/frame.v1/L1/1186988032/L-L1_GWOSC_O2_4KHZ_R1-1187008512-4096.gwf
        >>> cache.write(sys.stdout, format="basenames")
        L-L1_GWOSC_O2_4KHZ_R1-1187008512-4096.gwf
        """
        if isinstance(output, (str, PathLike)):
            with open(output, "w") as file:
                self.write(file)
                return
        for line in self._format_cache(format):
            print(line, file=output)
