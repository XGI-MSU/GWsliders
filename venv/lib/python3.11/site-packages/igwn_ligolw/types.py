# Copyright (C) 2006--2013,2016--2019,2021,2022  Kipp Cannon
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
Definitions of type strings found in LIGO Light Weight XML files.

Notes.  To guarantee that a double-precision floating-point number can be
reconstructed exactly from its representation as a decimal number, one must
use 17 decimal digits;  for single-precision, the number is 9.  Python uses
only double-precision numbers, but LIGO Light Weight XML allows for
single-precision values, so I provide distinct format specifiers for those
cases here.  In both cases, I have elected to use 1 fewer digits than are
required to uniquely reconstruct the number:  the XML written by this
library is lossy.  I made this choice to reduce the file size, for example

>>> "%.17g" % 0.1
'0.10000000000000001'

while

>>> "%.16g" % 0.1
'0.1'

In this worst case, storing full precision increases the size of the XML by
more than an order of magnitude.  If you wish to make a different choice
for your files, for example if you wish your XML files to be lossless,
simply include the lines::

        igwn_ligolw.types.FormatFunc.update({
                "real_4": "%.9g".__mod__,
                "real_8": "%.17g".__mod__,
                "float": "%.9g".__mod__,
                "double": "%.17g".__mod__,
                "complex_8": igwn_ligolw.types.mk_complex_format_func("%.9g"),
                "complex_16": igwn_ligolw.types.mk_complex_format_func("%.17g")
        })

anywhere in your code, but before you write the document to a file.

References:

        - http://docs.sun.com/source/806-3568/ncg_goldberg.html
"""

import base64

#
# =============================================================================
#
#                               Type Categories
#
# =============================================================================
#


BlobTypes = set(["blob", "ilwd:char_u"])
"""LIGO Light-Weight XML type strings for binary blob-like data."""

StringTypes = set(["char_s", "char_v", "lstring", "string", "ilwd:char"])
"""LIGO Light-Weight XML type strings for string-like data."""

IntTypes = set(["int_2s", "int_2u", "int_4s", "int_4u", "int_8s", "int_8u", "int"])
"""LIGO Light-Weight XML type strings for integer-like data."""

FloatTypes = set(["real_4", "real_8", "float", "double"])
"""LIGO Light-Weight XML type strings for floating-point-like data."""

ComplexTypes = set(["complex_8", "complex_16"])
"""LIGO Light-Weight XML type strings for complex-like data."""

NumericTypes = IntTypes | FloatTypes | ComplexTypes
"""LIGO Light-Weight XML type strings for number-like data."""

TimeTypes = set(["GPS", "Unix", "ISO-8601"])
"""LIGO Light-Weight XML type strings for time-like data."""

Types = BlobTypes | StringTypes | NumericTypes | TimeTypes
"""All valid LIGO Light-Weight XML type strings."""


#
# =============================================================================
#
#                         Output Format Look-up Table
#
# =============================================================================
#


def string_format_func(s):
    """
    Function used internally to format string data for output to XML.
    Escapes back-slashes and quotes, and wraps the resulting string in
    quotes.
    """
    return '"%s"' % str(s).replace("\\", "\\\\").replace('"', '\\"')


def blob_format_func(b):
    """
    Function used internally to format binary data.  Base64-encodes the
    data and wraps the resulting string in quotes.
    """
    return '"%s"' % base64.standard_b64encode(b)


def mk_complex_format_func(fmt):
    """
    Function used internally to generate functions to format complex
    valued data.
    """
    fmt = fmt + "+i" + fmt

    def complex_format_func(z):
        return fmt % (z.real, z.imag)

    return complex_format_func


FormatFunc = {
    "char_s": string_format_func,
    "char_v": string_format_func,
    "ilwd:char": '"%s"'.__mod__,
    "ilwd:char_u": blob_format_func,
    "blob": blob_format_func,
    "lstring": string_format_func,
    "string": string_format_func,
    "int_2s": "%d".__mod__,
    "int_2u": "%u".__mod__,
    "int_4s": "%d".__mod__,
    "int_4u": "%u".__mod__,
    "int_8s": "%d".__mod__,
    "int_8u": "%u".__mod__,
    "int": "%d".__mod__,
    "real_4": "%.8g".__mod__,
    "real_8": "%.16g".__mod__,
    "float": "%.8g".__mod__,
    "double": "%.16g".__mod__,
    "complex_8": mk_complex_format_func("%.8g"),
    "complex_16": mk_complex_format_func("%.16g"),
}
"""
Look-up table mapping LIGO Light-Weight XML data type strings to functions
for formating Python data for output.  This table is used universally by
igwn_ligolw XML writing codes.
"""


#
# =============================================================================
#
#                  Conversion To And From Native Python Types
#
# =============================================================================
#


ToPyType = {
    "char_s": str,
    "char_v": str,
    "ilwd:char": str,
    "ilwd:char_u": lambda s: memoryview(base64.b64decode(s)),
    "blob": lambda s: memoryview(base64.b64decode(s)),
    "lstring": str,
    "string": str,
    "int_2s": int,
    "int_2u": int,
    "int_4s": int,
    "int_4u": int,
    "int_8s": int,
    "int_8u": int,
    "int": int,
    "real_4": float,
    "real_8": float,
    "float": float,
    "double": float,
    "complex_8": lambda s: complex(*map(float, s.split("+i"))),
    "complex_16": lambda s: complex(*map(float, s.split("+i"))),
}
"""
Look-up table mapping LIGO Light-Weight XML data type strings to functions
for parsing Python data from input.  This table is used universally by
igwn_ligolw XML parsing codes.
"""


class FromPyTypeCls(dict):
    def __getitem__(self, key):
        try:
            return super(FromPyTypeCls, self).__getitem__(key)
        except KeyError:
            for test_key, val in self.items():
                if issubclass(key, test_key):
                    return val
            raise


FromPyType = FromPyTypeCls(
    {
        memoryview: "blob",
        str: "lstring",
        bool: "int_4s",
        int: "int_8s",
        float: "real_8",
        complex: "complex_16",
    }
)
"""
Look-up table used to guess LIGO Light-Weight XML data type strings from
Python types.  This table is used when auto-generating XML from Python
objects.

Python objects that are instances of one of the types in this look-up table
are mapped to the LIGO Light-Weight XML type indicated.  If a Python object
is not an instance of exactly one of the types in this look-up table, but
it is an instance of a subclass of one of these types, then it is treated
as that type and mapped to the corresponding LIGO Light-Weight XML type.
"""


#
# =============================================================================
#
#                  Conversion To and From Native Numpy Types
#
# =============================================================================
#


ToNumPyType = {
    "char_s": "U20",
    "char_v": "U64",
    "ilwd:char": "U64",
    "ilwd:char_u": "bytes",
    "blob": "bytes",
    "lstring": "U255",
    "string": "U255",
    "int_2s": "int16",
    "int_2u": "uint16",
    "int_4s": "int32",
    "int_4u": "uint32",
    "int_8s": "int64",
    "int_8u": "uint64",
    "int": "int32",
    "real_4": "float32",
    "real_8": "float64",
    "float": "float32",
    "double": "float64",
    "complex_8": "complex64",
    "complex_16": "complex128",
}
"""
Look-up table mapping LIGO Light-Weight XML data type strings to numpy
array type strings.  Used by igwn_ligolw array reading codes.
"""


FromNumPyType = {
    "int16": "int_2s",
    "uint16": "int_2u",
    "int32": "int_4s",
    "uint32": "int_4u",
    "int64": "int_8s",
    "uint64": "int_8u",
    "float32": "real_4",
    "float64": "real_8",
    "complex64": "complex_8",
    "complex128": "complex_16",
}
"""
Look-up table mapping numpy array type strings to LIGO Light-Weight XML
data type strings.  Uesd by igwn_ligolw array writing codes.
"""


#
# =============================================================================
#
#                 Conversion To and From Native Database Types
#
# =============================================================================
#


#
# SQL does not support complex numbers.  Documents containing
# complex-valued table columns cannot be stored in SQL databases at this
# time.
#


ToMySQLType = {
    "char_s": "CHAR(20)",
    "char_v": "VARCHAR(64)",
    "ilwd:char": "VARCHAR(64)",
    "ilwd:char_u": "BLOB",
    "blob": "BLOB",
    "lstring": "VARCHAR(255)",
    "string": "VARCHAR(255)",
    "int_2s": "SMALLINT",
    "int_2u": "SMALLINT",
    "int_4s": "INTEGER",
    "int_4u": "INTEGER",
    "int_8s": "BIGINT",
    "int_8u": "BIGINT",
    "int": "INTEGER",
    "real_4": "FLOAT",
    "real_8": "DOUBLE",
    "float": "FLOAT",
    "double": "DOUBLE",
}
"""
Look-up table mapping LIGO Light-Weight XML data type strings to MySQL
column types.  Used by XML --> MySQL conversion codes.
"""


ToSQLiteType = {
    "char_s": "TEXT",
    "char_v": "TEXT",
    "ilwd:char": "TEXT",
    "ilwd:char_u": "BLOB",
    "blob": "BLOB",
    "lstring": "TEXT",
    "string": "TEXT",
    "int_2s": "INTEGER",
    "int_2u": "INTEGER",
    "int_4s": "INTEGER",
    "int_4u": "INTEGER",
    "int_8s": "INTEGER",
    "int_8u": "INTEGER",
    "int": "INTEGER",
    "real_4": "REAL",
    "real_8": "REAL",
    "float": "REAL",
    "double": "REAL",
}
"""
Look-up table mapping LIGO Light-Weight XML data type strings to SQLite
column types.  Used by XML --> SQLite conversion codes.
"""


FromSQLiteType = {
    "BLOB": "blob",
    "TEXT": "lstring",
    "STRING": "lstring",
    "INTEGER": "int_4s",
    "REAL": "real_8",
}
"""
Look-up table used to guess LIGO Light-Weight XML data type strings from
SQLite column types.  Used when auto-generating XML from the contents of an
SQLite database.
"""
