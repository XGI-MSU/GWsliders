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

"""Tests for :mod:`gwdatafind.utils`."""

from unittest import mock

import pytest

from gwdatafind import utils


@mock.patch.dict(
    "os.environ",
    {
        "GWDATAFIND_SERVER": "gwtest",
        "LIGO_DATAFIND_SERVER": "ligotest",
    },
)
def test_get_default_host():
    """Test `get_default_host()` with both environment variables."""
    assert utils.get_default_host() == "gwtest"


@mock.patch.dict(
    "os.environ",
    {"LIGO_DATAFIND_SERVER": "ligotest"},
    clear=True,
)
def test_get_default_host_ligo():
    """Test `get_default_host()` with ``LIGO_DATAFIND_SERVER`` env only."""
    assert utils.get_default_host() == "ligotest"


@mock.patch.dict("os.environ", clear=True)
def test_get_default_host_error():
    """Test `get_default_host()` error handling."""
    with pytest.raises(
        ValueError,
        match="Failed to determine default gwdatafind host",
    ):
        utils.get_default_host()


@mock.patch(
    "igwn_auth_utils.x509.validate_certificate",
    side_effect=(None, RuntimeError),
)
def test_validate_proxy(mock_validate):
    """Test `validate_proxy()`."""
    # check that no error ends up as 'True'
    with pytest.warns(DeprecationWarning):
        assert utils.validate_proxy("something") is True
    # but that an error is forwarded
    with pytest.warns(DeprecationWarning), pytest.raises(RuntimeError):
        assert utils.validate_proxy("something else")


@mock.patch(
    "igwn_auth_utils.x509.find_credentials",
    side_effect=("cert", ("cert", "key")),
)
def test_find_credential(mock_find_credentials):
    """Test `find_credential()`."""
    # check that if upstream returns a single cert, we still get a tuple
    with pytest.warns(DeprecationWarning):
        assert utils.find_credential() == ("cert", "cert")
    # but if it returns a tuple, we get a tuple
    with pytest.warns(DeprecationWarning):
        assert utils.find_credential() == ("cert", "key")
