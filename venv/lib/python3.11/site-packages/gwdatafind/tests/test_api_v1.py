# Copyright (c) 2025 Cardiff University
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

"""Test suite for `gwdatafind.api.v1`.

This just asserts that the API implementation here matches the expectation
from the v1 API for gwdatfind_server.
"""

import pytest

from gwdatafind.api import v1 as api_v1

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"


def test_ping_path():
    """Test `ping_path()`."""
    assert api_v1.ping_path() == "api/version"


@pytest.mark.parametrize(("kwargs", "result"), [
    pytest.param(
        {},
        "gwf.json",
        id="default",
    ),
    pytest.param(
        {"ext": "gwf"},
        "gwf.json",
        id="gwf",
    ),
    pytest.param(
        {"ext": "hdf5"},
        "hdf5.json",
        id="hdf5",
    ),
])
def test_find_observatories_path(kwargs, result):
    """Test `find_observatories_path()`."""
    assert api_v1.find_observatories_path(**kwargs) == f"api/v1/{result}"


@pytest.mark.parametrize(("args", "kwargs", "result"), [
    pytest.param(
        (None,),
        {},
        "gwf/all.json",
        id="all",
    ),
    pytest.param(
        ("X",),
        {},
        "gwf/X.json",
        id="X",
    ),
    pytest.param(
        (),
        {"site": "XY", "ext": "hdf5"},
        "hdf5/XY.json",
        id="XY",
    ),
])
def test_find_types_path(args, kwargs, result):
    """Test `find_types_path()`."""
    assert api_v1.find_types_path(*args, **kwargs) == f"api/v1/{result}"


@pytest.mark.parametrize(("args", "kwargs", "result"), [
    pytest.param(
        ("X", "TEST", 0, 1),
        {},
        "gwf/X/TEST/segments/0,1.json",
        id="X-TEST-default",
    ),
    pytest.param(
        ("X", "TEST", 1000, 2000),
        {"ext": "gwf"},
        "gwf/X/TEST/segments/1000,2000.json",
        id="X-TEST-gwf",
    ),
    pytest.param(
        ("XY", "TEST", 0, 1),
        {"ext": "hdf5"},
        "hdf5/XY/TEST/segments/0,1.json",
        id="XY-TEST-hdf5",
    ),
])
def test_find_times_path(args, kwargs, result):
    """Test `find_times_path()`."""
    assert api_v1.find_times_path(*args, **kwargs) == f"api/v1/{result}"


@pytest.mark.parametrize(("args", "result"), [
    pytest.param(
        ("/data/X-TEST-0-1.gwf",),
        "gwf/X/TEST/X-TEST-0-1.gwf.json",
        id="gwf",
    ),
    pytest.param(
        ("/data/XY-TEST-1000-2000.hdf5",),
        "hdf5/XY/TEST/XY-TEST-1000-2000.hdf5.json",
        id="hdf5",
    ),
])
def test_find_url_path(args, result):
    """Test `find_url_path()`."""
    assert api_v1.find_url_path(*args) == f"api/v1/{result}"


@pytest.mark.parametrize(("args", "kwargs", "result"), [
    pytest.param(
        ("X", "TEST", None),
        {},
        "gwf/X/TEST/latest.json",
        id="default",
    ),
    pytest.param(
        ("X", "TEST", "file"),
        {},
        "gwf/X/TEST/latest/file.json",
        id="file",
    ),
    pytest.param(
        ("X", "TEST", "file"),
        {"ext": "hdf5"},
        "hdf5/X/TEST/latest/file.json",
        id="hdf5-file",
    ),
])
def test_find_latest_path(args, kwargs, result):
    """Test `find_latest_path()`."""
    assert api_v1.find_latest_path(*args, **kwargs) == f"api/v1/{result}"


@pytest.mark.parametrize(("args", "kwargs", "result"), [
    pytest.param(
        ("X", "TEST", 0, 1),
        {},
        "gwf/X/TEST/0,1.json",
        id="default",
    ),
    pytest.param(
        ("X", "TEST", 0, 1),
        {"urltype": "gsiftp", "ext": "hdf5"},
        "hdf5/X/TEST/0,1/gsiftp.json",
        id="hdf5-gsiftp",
    ),
    pytest.param(
        ("XY", "TEST", 0, 1),
        {"match": "test"},
        "gwf/XY/TEST/0,1.json?match=test",
        id="match",
    ),
    pytest.param(
        ("X", "TEST", 0, 1),
        {"urltype": "file", "match": "test", "ext": "gwf"},
        "gwf/X/TEST/0,1/file.json?match=test",
        id="gwf-file-match",
    ),
])
def test_find_urls_path(args, kwargs, result):
    """Test `find_urls_path()`."""
    assert api_v1.find_urls_path(*args, **kwargs) == f"api/v1/{result}"
