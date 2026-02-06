# Copyright (C) 2006--2013,2015,2017,2019,2020  Kipp Cannon
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
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
A collection of utilities to assist applications in manipulating the
process and process_params tables in LIGO Light-Weight XML documents.
"""

import warnings

from .. import lsctables

#
# =============================================================================
#
#                               Process Metadata
#
# =============================================================================
#


def get_process_params(xmldoc, program, param, require_unique_program=True):
    """
    Return a list of the values stored in the process_params table for
    params named param for the program(s) named program.  The values
    are returned as Python native types, not as the strings appearing
    in the XML document.  If require_unique_program is True (default),
    then the document must contain exactly one program with the
    requested name, otherwise ValueError is raised.  If
    require_unique_program is not True, then there must be at least one
    program with the requested name otherwise ValueError is raised.
    """
    process_ids = lsctables.ProcessTable.get_table(xmldoc).get_ids_by_program(program)
    if len(process_ids) < 1:
        raise ValueError(
            "process table must contain at least one program named '%s'" % program
        )
    elif require_unique_program and len(process_ids) != 1:
        raise ValueError(
            "process table must contain exactly one program named '%s'" % program
        )
    return [
        row.pyvalue
        for row in lsctables.ProcessParamsTable.get_table(xmldoc)
        if (row.process_id in process_ids) and (row.param == param)
    ]


def doc_includes_process(xmldoc, program):
    """
    Return True if the process table in xmldoc includes entries for a
    program named program.
    """
    return program in lsctables.ProcessTable.get_table(xmldoc).getColumnByName(
        "program"
    )


def register_to_xmldoc(xmldoc, *args, **kwargs):
    warnings.warn(
        "igwn_ligolw.utils.process.register_to_xmldoc() is deprecated.  use igwn_ligolw.ligolw.Document.register_process() instead."
    )
    return xmldoc.register_process(*args, **kwargs)
