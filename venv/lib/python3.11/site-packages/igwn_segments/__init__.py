# Copyright (C) 2006  Kipp Cannon
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


#
# =============================================================================
#
#                                   Preamble
#
# =============================================================================
#


#
# NOTE:  the logic in this code is unintuitively complicated.  Small,
# apparently irrelevant, changes to conditionals can have subtly unexpected
# consequences to the behaviour of the class methods.  ALWAYS make sure that
# the test suite returns OK on ALL tests after any changes you make.
#


"""
Representations of semi-open intervals.

This package provides the `segment` and `segmentlist` objects,
as well as the `infinity` object used to define semi-infinite
and infinite segments.
"""

import copyreg

from ._segments_c import NegInfinity, PosInfinity, infinity, segment, segmentlist
from ._segments_py import segmentlistdict
from ._version import __version__

__author__ = "Kipp Cannon <kipp.cannon@ligo.org>"

__all__ = [
    "infinity",
    "PosInfinity",
    "NegInfinity",
    "segment",
    "segmentlist",
    "segmentlistdict",
]


# =============================================================================
#
#                                Pickle Support
#
# =============================================================================
#


copyreg.pickle(segment, lambda x: (segment, tuple(x)))
copyreg.pickle(segmentlist, lambda x: (segmentlist, (), None, iter(x)))
