# Copyright (C) 2006--2021  Kipp Cannon
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


"""
Deprecated.  Do not use.  The Column and Table classes in ligolw now
implement the features previously found here.
"""

import warnings

# temporary compatibility stubs
from .ligolw import LIGO_LW, Column, Table

warnings.warn(
    "igwn_ligolw.table module is deprecated.  the features previously implemented by the Column and Table classes in this module are now implemented natively by the classes in the igwn_ligolw.ligolw module proper.  this module will be removed in the next release."
)

next_id = Column.next_id


def reassign_ids(elem):
    LIGO_LW.reassign_table_row_ids(elem)


TableStream = Table.Stream


def use_in(ContentHandler):
    warnings.warn(
        "igwn_ligolw.table module is deprecated.  the features previously implemented by the Column and Table classes in this module are now implemented natively by the classes in the igwn_ligolw.ligolw module proper.  this module will be removed in the next release."
    )
    return ContentHandler
