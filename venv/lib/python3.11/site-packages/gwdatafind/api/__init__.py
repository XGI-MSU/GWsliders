# Copyright (C) 2025 Cardiff University
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
# along with GWDataFind.  If not, see <http://www.gnu.org/licenses/>.

"""API definitions for the GWDataFind Client.

Each API module must define the same set of functions that
return paths to be queried on the host to return the various
endpoints.

The required functions and signatures are:

- ``ping_path()``
- ``find_observatories_path()``
- ``find_types_path(site=None)``
- ``find_times_path(site, frametype, start, end)``
- ``find_url_path(framefile)``
- ``find_latest_path(site, frametype, urltype)``
- ``find_urls_path(site, frametype, start, end, urltype=None, match=None)``
"""

import os

#: List of supported APIs
APIS = (
    "ldr",
    "v1",
)

#: Default API version when not specified
_DEFAULT_API = "v1"

#: Default API version to use
DEFAULT_API = os.getenv("GWDATAFIND_API", _DEFAULT_API)
