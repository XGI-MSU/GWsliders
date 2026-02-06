# Copyright (C) 2006,2007,2009,2011,2013,2016-2021  Kipp Cannon
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
DOM-like library for handling LIGO Light Weight XML files.  For more
information on the Python DOM specification and SAX document content
handlers, please refer to the Python standard library reference and the
documentation it links to.

Here is a brief tutorial for a common use case:  load a LIGO Light-Weight
XML document containing tabular data complying with the LSC table
definitions, access rows in the tables including the use of ID-based cross
references, modify the contents of a table, and finally write the document
back to disk.  Please see the documentation for the modules, classes,
functions, and methods shown below for more information.

Example:

>>> # import modules
>>> from igwn_ligolw import ligolw
>>> from igwn_ligolw import lsctables
>>> from igwn_ligolw import utils as ligolw_utils
>>>
>>> # load a document.  several compressed file formats are recognized
>>> filename = "demo.xml.gz"
>>> xmldoc = ligolw_utils.load_filename(filename, verbose = True)
>>>
>>> # retrieve the process and sngl_inspiral tables.  these are list-like
>>> # objects of rows.  the row objects' attributes are the column names
>>> process_table = lsctables.ProcessTable.get_table(xmldoc)
>>> sngl_inspiral_table = lsctables.SnglInspiralTable.get_table(xmldoc)
>>>
>>> # fix the mtotal column in the sngl_inspiral table
>>> for row in sngl_inspiral_table:
...	row.mtotal = row.mass1 + row.mass2
...
>>> # construct a look-up table mapping process_id to row in process table
>>> index = dict((row.process_id, row) for row in process_table)
>>>
>>> # for each trigger in the sngl_inspiral table, print the name of the user
>>> # who ran the job that produced it, the computer on which the job ran, and
>>> # the GPS end time of the trigger
>>> for row in sngl_inspiral_table:
...	process = index[row.process_id]
...	print "%s@%s: %s s" % (process.username, process.node, str(row.end))
...
>>> # write document.  the file is automatically compressed because its name
>>> # ends with .gz, and several other compression formats are also supported
>>> ligolw_utils.write_filename(xmldoc, filename, verbose = True)

Version 2 Notes:

The LIGO Light-Weight XML document format has two specification documents:

- `LIGO-T980091 <https://dcc.ligo.org/LIGO-T980091/public>`_
- `LIGO-P000010 <https://dcc.ligo.org/LIGO-P000010/public>`_

In practice, it is mostly defined by active implementations, which include
this library as well as the following:

- https://git.ligo.org/lscsoft/metaio
- https://git.ligo.org/lscsoft/lalsuite/-/tree/master/lalmetaio
- https://git.ligo.org/cds/software/dtt

Those implementations have differed in incompatible ways in the past, and
might still do so today.  Historically, this library made an effort to be
as flexible as possible with regard to the document content to allow
documents compatible with all other I/O libraries to be read and written.
The only true requirement imposed by this library was that documents were
required to be valid XML and comply with the DTD (when that was supplied).
Aspects of the file format outside the scope of XML itself, for example how
to encode a choice of units in a Dim element, did not necessarily have a
strict specification imposed, but as a consequence high-level features
could not be implemented because it wasn't possible to ensure input
documents would comply with the necessary format assumptions.  To implement
more convenient high-level support for the document contents, for example
to cause this libray to treat Table elements as containing tabular data
instead of blocks of text, calling codes were required to explicitly enable
additional parsing rules by constructing a suitable content handler object
(the object responsible for translating XML components to the corresponding
Python objects).  This required numerous module imports and cryptic symbol
declarations, often for reasons that weren't clear to users of the library.
Over time the number of users of this file format has dwindled, and since
the user community that remains works exclusively with documents that
comply with the high-level format assumptions of this library, the
motivation has evaporated for continuing to inconvenience those remaining
users with the cryptic imports and configuration boilerplate required to
support other hypothetical users working with non-compliant documents.
Therefore, starting with version 2.0 that flexibility was removed.  All
documents processed with this library are now required to comply with the
file format defined by this library.  Removing the flexibility increases
document loading speed, and makes calling codes simpler, and less sensitive
to future API changes."""

from ._version import version as __version__

__author__ = "Kipp Cannon <kipp@g.ecc.u-tokyo.ac.jp>"

__all__ = [
    "ligolw",
    "lsctables",
    "types",
    "utils",
]

__doctest_skip__ = ["*"]
