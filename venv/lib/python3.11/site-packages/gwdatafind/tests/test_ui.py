# Copyright (C) 2018-2025 Cardiff University
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

"""Test :mod:`gwdatafind.ui`."""

import warnings
from contextlib import contextmanager
from functools import partial
from math import (
    ceil,
    floor,
)
from unittest import mock

import igwn_segments as segments
import pytest

from gwdatafind import ui
from gwdatafind.api import v1 as api

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

TEST_SERVER = "test.datafind.org"
TEST_API = "v1"
TEST_URL_BASE = f"https://{TEST_SERVER}"
TEST_DATA = {
    "A": {
        "A1_TEST": [(0, 10), (10, 20), (30, 50)],
        "A2_TEST": [],
        "A1_PROD": [],
    },
    "B": {
        "B1_TEST",
    },
    "C": {
        "C1_TEST",
    },
}

# partials with the TEST_API set by default:
find_url = partial(ui.find_url, api=TEST_API)
find_urls = partial(ui.find_urls, api=TEST_API)


@contextmanager
def no_warning():
    """Context manager to ensure no warnings are emitted."""
    with warnings.catch_warnings() as ctx:
        warnings.simplefilter("error")
        yield ctx


def _url(suffix):
    """Return a fully-qualified URL with the given suffix."""
    return f"{TEST_URL_BASE}/{suffix}"


@pytest.fixture(autouse=True)
def gwdatafind_server_env():
    """Patch `os.environ` with our value for ``GWDATAFIND_SERVER``."""
    with mock.patch.dict(
        "os.environ",
        {"GWDATAFIND_SERVER": TEST_SERVER},
    ):
        yield


@pytest.fixture(autouse=True, scope="module")
def noauth():
    """Force the underlying _get() function to use no authentication.

    So that the tests don't fall over if the test runner has bad creds.
    """
    with mock.patch(
        "gwdatafind.ui._get",
        partial(ui._get, cert=False, token=False),  # noqa: SLF001
    ):
        yield


@pytest.mark.parametrize(("in_", "url"), [
    # no scheme and no port, default to https
    pytest.param(
        "datafind.example.com",
        "https://datafind.example.com",
        id="scheme-default",
    ),
    # scheme specified, do nothing
    pytest.param(
        "test://datafind.example.com",
        "test://datafind.example.com",
        id="scheme-noop",
    ),
    pytest.param(
        "test://datafind.example.com:1234",
        "test://datafind.example.com:1234",
        id="port-noop",
    ),
    pytest.param(
        "https://datafind.example.com:80",
        "https://datafind.example.com:80",
        id="scheme-port-noop",
    ),
    # no scheme and port 80, use http
    pytest.param(
        "datafind.example.com:80",
        "http://datafind.example.com:80",
        id="scheme-port-http",
    ),
    # no scheme and port != 80, use https
    pytest.param(
        "datafind.example.com:443",
        "https://datafind.example.com:443",
        id="scheme-port-https",
    ),
    # default host
    pytest.param(
        None,
        TEST_URL_BASE,
        id="default-host",
    ),
])
@mock.patch("gwdatafind.ui._api_func")
def test_url_scheme_handling(mock_api_func, in_, url):
    """Test URL scheme handling in `_url()`."""
    def func(*args):
        return "/".join(args)

    mock_api_func.return_value = func
    assert ui._url(in_, "api", "funcname", "x", "y") == f"{url}/x/y"  # noqa: SLF001


def test_ping(requests_mock):
    """Test `ping()`."""
    requests_mock.get(
        _url(api.ping_path()),
        status_code=200,
        json={"api_versions": ["v1", "ldr"], "version": "1.2.3"},
    )
    response = ui.ping(api=TEST_API)
    assert response["version"] == "1.2.3"


@pytest.mark.parametrize(("match", "result"), [
    pytest.param(None, ("A", "B", "C"), id="all"),
    pytest.param("[AB]", ("A", "B"), id="regex"),
])
def test_find_observatories(match, result, requests_mock):
    """Test `find_observatories()`."""
    requests_mock.get(
        _url(api.find_observatories_path()),
        json=list(TEST_DATA),
    )
    assert ui.find_observatories(
        api=TEST_API,
        match=match,
    ) == list(set(result))


@pytest.mark.parametrize(("site", "match", "result"), [
    pytest.param(
        None,
        None,
        [ft for site in TEST_DATA for ft in TEST_DATA[site]],
        id="all",
    ),
    pytest.param(
        "A",
        None,
        list(TEST_DATA["A"]),
        id="site",
    ),
    pytest.param(
        "A",
        "PROD",
        ["A1_PROD"],
        id="site-match",
    ),
])
def test_find_types(site, match, result, requests_mock):
    """Test `find_types()`."""
    if site:
        respdata = list(TEST_DATA[site])
    else:
        respdata = [ft for site in TEST_DATA for ft in TEST_DATA[site]]
    requests_mock.get(
        _url(api.find_types_path(site=site)),
        json=respdata,
    )
    assert ui.find_types(
        api=TEST_API,
        site=site,
        match=match,
    ) == list(set(result))


def test_find_times(requests_mock):
    """Test `find_times()`."""
    site = "A"
    frametype = "A1_TEST"
    requests_mock.get(
        _url(api.find_times_path(site, frametype, 1, 100)),
        json=TEST_DATA[site][frametype],
    )
    assert ui.find_times(
        site,
        frametype,
        1,
        100,
        api=TEST_API,
    ) == segments.segmentlist([
        segments.segment(0, 10),
        segments.segment(10, 20),
        segments.segment(30, 50),
    ])


def test_find_url(requests_mock):
    """Test `find_url()`."""
    urls = [
        "file:///data/A/A1_TEST/A-A1_TEST-0-1.gwf",
        "gsiftp://localhost:2811/data/A/A1_TEST/A-A1_TEST-0-1.gwf",
    ]
    requests_mock.get(
        _url(api.find_url_path("A-A1_TEST-0-1.gwf")),
        json=urls,
    )
    assert find_url("/my/data/A-A1_TEST-0-1.gwf") == urls[:1]
    assert find_url("/my/data/A-A1_TEST-0-1.gwf", urltype=None) == urls
    assert find_url(
        "/my/data/A-A1_TEST-0-1.gwf",
        urltype="gsiftp",
    ) == urls[1:]


@pytest.mark.parametrize(("on_missing", "ctx"), [
    # no warnings, no errors
    pytest.param("ignore", no_warning(), id="ignore"),
    # a warning about validation
    pytest.param(
        "warn",
        pytest.warns(
            UserWarning,
            match="no files found",
        ),
        id="warn",
    ),
    # an exception about validation
    pytest.param(
        "raise",
        pytest.raises(
            RuntimeError,
            match="no files found",
        ),
        id="raise",
    ),
])
def test_find_url_on_missing(requests_mock, on_missing, ctx):
    """Test `find_url` handling of missing data."""
    # mock the request
    requests_mock.get(
        _url(api.find_url_path("A-A1_TEST-0-1.gwf")),
        json=[],
    )

    with ctx:
        assert find_url(
            "A-A1_TEST-0-1.gwf",
            on_missing=on_missing,
        ) == []


def test_find_latest(requests_mock):
    """Test `find_latest()`."""
    # NOTE: the target function is essentially identical to
    #       find_url, so we just do a minimal smoke test here
    urls = [
        "file:///data/A/A1_TEST/A-A1_TEST-0-1.gwf",
        "gsiftp://localhost:2811/data/A/A1_TEST/A-A1_TEST-0-1.gwf",
    ]
    requests_mock.get(
        _url(api.find_latest_path("A", "A1_TEST", "file")),
        json=urls[:1],
    )
    assert ui.find_latest(
        "A",
        "A1_TEST",
        api=TEST_API,
    ) == urls[:1]


def _file_url(seg):
    seg = segments.segment(floor(seg[0]), ceil(seg[1]))
    return f"file:///data/A/A1_TEST/A-A1_TEST-{seg[0]}-{abs(seg)}.gwf"


def test_find_urls(requests_mock):
    """Test `find_urls()`."""
    urls = list(map(_file_url, TEST_DATA["A"]["A1_TEST"][:2]))
    requests_mock.get(
        _url(api.find_urls_path("A", "A1_TEST", 0, 20, "file")),
        json=urls,
    )
    assert find_urls("A", "A1_TEST", 0, 20, on_gaps="error") == urls


@pytest.mark.parametrize(("on_gaps", "ctx"), [
    # no warnings, no errors
    pytest.param("ignore", no_warning(), id="ignore"),
    # a warning about validation
    pytest.param(
        "warn",
        pytest.warns(
            UserWarning,
            match="^Missing segments",
        ),
        id="warn",
    ),
    # an exception about validation
    pytest.param(
        "raise",
        pytest.raises(
            RuntimeError,
            match=r"^Missing segments",
        ),
        id="raise",
    ),
])
def test_find_urls_on_gaps(requests_mock, on_gaps, ctx):
    """Test `find_urls` handling of gaps with ``on_gaps``."""
    # configure the mock request
    urls = list(map(_file_url, TEST_DATA["A"]["A1_TEST"]))
    requests_mock.get(
        _url(api.find_urls_path("A", "A1_TEST", 0, 100, "file")),
        json=urls,
    )

    # make the request
    with ctx:
        assert find_urls(
            "A",
            "A1_TEST",
            0,
            100,
            on_gaps=on_gaps,
        ) == urls
