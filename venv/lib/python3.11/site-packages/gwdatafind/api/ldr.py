# Copyright (C) 2012-2015 University of Wisconsin-Milwaukee
#               2015-2017 Louisiana State University
#               2017-2025 Cardiff University
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

"""API URL implementation for GWDataFind.

The functions in this module return URL paths to request on a given host
to execute various GWDataFind queries.
"""

from functools import wraps
from os.path import basename

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

DEFAULT_EXT = "gwf"
DEFAULT_SERVICE_PREFIX = "LDR/services/data/v1"


def _prefix(func):
    """Wrap ``func`` to prepend the path prefix automatically.

    This just simplifies the functional constructions below.
    """
    @wraps(func)
    def wrapped(*args, **kwargs):
        prefix = kwargs.pop("prefix", DEFAULT_SERVICE_PREFIX)
        suffix = func(*args, **kwargs)
        return f"{prefix}/{suffix}"

    return wrapped


@_prefix
def ping_path(ext=DEFAULT_EXT):
    """Return the API path to ping the server."""
    return f"{ext}/H/R/1,2"


@_prefix
def find_observatories_path(ext=DEFAULT_EXT):
    """Return the API path to query for all observatories."""
    return f"{ext}.json"


@_prefix
def find_types_path(site=None, ext=DEFAULT_EXT):
    """Return the API path to query for datasets for one or all sites."""
    if site:
        return f"{ext}/{site}.json"
    return f"{ext}/all.json"


@_prefix
def find_times_path(site, frametype, start, end, ext=DEFAULT_EXT):
    """Return the API path to query for data availability segments."""
    if start is None and end is None:
        return f"{ext}/{site}/{frametype}/segments.json"
    return f"{ext}/{site}/{frametype}/segments/{start},{end}.json"


@_prefix
def find_url_path(framefile):
    """Return the API path to query for the URL of a specific filename."""
    filename = basename(framefile)
    ext = filename.split(".", 1)[1]
    site, frametype, _ = filename.split("-", 2)
    return f"{ext}/{site}/{frametype}/{filename}.json"


@_prefix
def find_latest_path(site, frametype, urltype, ext=DEFAULT_EXT):
    """Return the API path to query for the latest file in a dataset."""
    stub = f"{ext}/{site}/{frametype}/latest"
    if urltype:
        return f"{stub}/{urltype}.json"
    return stub + ".json"


@_prefix
def find_urls_path(
    site,
    frametype,
    start,
    end,
    urltype=None,
    match=None,
    ext=DEFAULT_EXT,
):
    """Return the API path to query for all URLs for a dataset in an interval."""
    stub = f"{ext}/{site}/{frametype}/{start},{end}"
    if urltype:
        path = f"{stub}/{urltype}.json"
    else:
        path = stub + ".json"
    if match:
        path += f"?match={match}"
    return path
