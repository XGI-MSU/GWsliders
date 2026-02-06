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

"""Tests for :mod:`gwdatafind.__main__` (the CLI)."""

import argparse
import os
from io import StringIO
from unittest import mock

import pytest
from igwn_segments import segment

from gwdatafind import __main__ as main

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

URLS = [
    "file:///test/X-test-0-1.gwf",
    "file:///test/X-test-1-1.gwf",
    "file:///test2/X-test-2-1.gwf",
    "file:///test2/X-test-7-4.gwf",
    "file:///test/X-test-0-1.h5",
    "file:///test/X-test-1-1.h5",
]
GWF_URLS = [url for url in URLS if url.endswith(".gwf")]
GWF_OUTPUT_URLS = """
file:///test/X-test-0-1.gwf
file:///test/X-test-1-1.gwf
file:///test2/X-test-2-1.gwf
file:///test2/X-test-7-4.gwf
"""[1:]  # strip leading line return
GWF_OUTPUT_LAL_CACHE = """
X test 0 1 file:///test/X-test-0-1.gwf
X test 1 1 file:///test/X-test-1-1.gwf
X test 2 1 file:///test2/X-test-2-1.gwf
X test 7 4 file:///test2/X-test-7-4.gwf
"""[1:]
GWF_OUTPUT_NAMES_ONLY = """
/test/X-test-0-1.gwf
/test/X-test-1-1.gwf
/test2/X-test-2-1.gwf
/test2/X-test-7-4.gwf
"""[1:]
GWF_OUTPUT_OMEGA_CACHE = """
X test 0 2 1 file:///test
X test 2 3 1 file:///test2
X test 7 11 4 file:///test2
"""[1:]
GAPS = [(3, 7)]


@mock.patch.dict(os.environ, {"GWDATAFIND_SERVER": "something"})
def test_command_line():
    """Test `command_line()`."""
    parser = main.command_line()
    assert isinstance(parser, argparse.ArgumentParser)
    assert parser.description == main.__doc__
    for query in ("ping", "show_observatories", "show_types", "show_times",
                  "filename", "latest"):
        assert not parser.get_default(query)
    assert parser.get_default("server") == os.getenv("GWDATAFIND_SERVER")
    assert parser.get_default("url_type") == "file"
    assert parser.get_default("gaps") is False

    # test parsing and types
    args = parser.parse_args([
        "-o", "X", "-t", "test", "--gps-start-time", "0", "-e", "1",
    ])
    assert args.gpsstart == 0.
    assert args.gpsend == 1.
    assert args.server == "something"


@mock.patch.dict("os.environ", clear=True)
@pytest.mark.parametrize("defserv", [None, "test.datafind.com:443"])
def test_command_line_server(defserv):
    """Test default setting for ``-r/--server``."""
    if defserv:
        os.environ["GWDATAFIND_SERVER"] = defserv
    parser = main.command_line()
    serveract = next(act for act in parser._actions if act.dest == "server")
    assert serveract.required is (not defserv)


@mock.patch.dict(os.environ, {"GWDATAFIND_SERVER": "something"})
def test_sanity_check_pass():
    """Test `DataFindArgumentParser.sanity_check()`."""
    parser = main.command_line()
    parser.parse_args(["-o", "X", "-t", "test", "-s", "0", "-e", "1"])


@mock.patch.dict(os.environ, {"GWDATAFIND_SERVER": "something"})
@pytest.mark.parametrize("clargs", [
    ("--show-times", "--observatory", "X"),
    ("--show-times", "--type", "test"),
    ("--type", "test", "--observatory", "X", "--gps-start-time", "1"),
    ("--gaps", "--show-observatories"),
])
def test_sanity_check_fail(clargs):
    """Test `DataFindArgumentParser.sanity_check()` error reporting."""
    parser = main.command_line()
    with pytest.raises(
        SystemExit,
        match="2",
    ):
        parser.parse_args(clargs)


def test_ping(requests_mock):
    """Test `ping()."""
    requests_mock.get(
        "https://test.datafind.com:443/api/version",
        json={"version": "1.2.3"},
    )
    args = argparse.Namespace(
        server="test.datafind.com:443",
        api="v1",
        extension="gwf",
    )
    out = StringIO()
    main.ping(args, out)
    out.seek(0)
    assert out.read().rstrip() == (
        "GWDataFind Server v1.2.3 at test.datafind.com:443 is alive"
    )


@mock.patch("gwdatafind.ui.find_observatories")
def test_show_observatories(mfindobs):
    """Test `show_observatories()."""
    mfindobs.return_value = ["A", "B", "C"]
    args = argparse.Namespace(
        server="test.datafind.com:443",
        api="v1",
        extension="gwf",
        match="test",
    )
    out = StringIO()
    main.show_observatories(args, out)
    out.seek(0)
    mfindobs.assert_called_with(
        host=args.server,
        api=args.api,
        match=args.match,
        ext=args.extension,
    )
    assert list(map(str.rstrip, out.readlines())) == ["A", "B", "C"]


@mock.patch("gwdatafind.ui.find_types")
def test_show_types(mfindtypes):
    """Test `show_types()."""
    mfindtypes.return_value = ["A", "B", "C"]
    args = argparse.Namespace(
        server="test.datafind.com:443",
        api="v1",
        extension="gwf",
        observatory="X",
        match="test",
    )
    out = StringIO()
    main.show_types(args, out)
    out.seek(0)
    mfindtypes.assert_called_with(
        host=args.server,
        api=args.api,
        match=args.match,
        site=args.observatory,
        ext=args.extension,
    )
    assert list(map(str.rstrip, out.readlines())) == ["A", "B", "C"]


@mock.patch("gwdatafind.ui.find_times")
def test_show_times(mfindtimes):
    """Test `show_times()."""
    mfindtimes.return_value = [segment(0, 1), segment(1, 2), segment(3, 4)]
    args = argparse.Namespace(
        server="test.datafind.com:443",
        api="v1",
        extension="gwf",
        observatory="X",
        type="test",
        gpsstart=0,
        gpsend=10,
    )
    out = StringIO()
    main.show_times(args, out)
    mfindtimes.assert_called_with(
        host=args.server,
        api=args.api,
        site=args.observatory,
        frametype=args.type,
        gpsstart=args.gpsstart,
        gpsend=args.gpsend,
        ext=args.extension,
    )
    out.seek(0)
    for i, line in enumerate(out.readlines()[1:]):
        seg = mfindtimes.return_value[i]
        assert line.split() == list(map(str, (i, seg[0], seg[1], abs(seg))))


@mock.patch("gwdatafind.ui.find_latest")
def test_latest(mlatest):
    """Test `latest()`."""
    mlatest.return_value = ["file:///test/X-test-0-10.gwf"]
    args = argparse.Namespace(
        server="test.datafind.com:443",
        api="v1",
        extension="gwf",
        observatory="X",
        type="test",
        url_type="file",
        format="urls",
        gaps=None,
    )
    out = StringIO()
    main.latest(args, out)
    mlatest.assert_called_with(
        args.observatory,
        args.type,
        urltype=args.url_type,
        on_missing="warn",
        host=args.server,
        api=args.api,
        ext=args.extension,
    )
    out.seek(0)
    assert out.read().rstrip() == mlatest.return_value[0]


@mock.patch("gwdatafind.ui.find_url")
def test_filename(mfindurl):
    """Test `filename()`."""
    mfindurl.return_value = ["file:///test/X-test-0-10.gwf"]
    args = argparse.Namespace(
        server="test.datafind.com:443",
        api="v1",
        filename="X-test-0-10.gwf",
        url_type="file",
        type=None,
        format="urls",
        gaps=None,
    )
    out = StringIO()
    main.filename(args, out)
    mfindurl.assert_called_with(
        args.filename,
        urltype=args.url_type,
        on_missing="warn",
        host=args.server,
        api=args.api,
    )
    out.seek(0)
    assert out.read().rstrip() == mfindurl.return_value[0]


@mock.patch("gwdatafind.ui.find_urls")
@pytest.mark.parametrize("ext", [
    "gwf",
    "h5",
])
def test_show_urls(mfindurls, ext):
    """Test `show_urls()`."""
    urls = [x for x in URLS if x.endswith(f".{ext}")]
    mfindurls.return_value = urls
    args = argparse.Namespace(
        server="test.datafind.com:443",
        api="v1",
        extension=ext,
        observatory="X",
        type="test",
        gpsstart=0,
        gpsend=10,
        url_type="file",
        match=None,
        format="urls",
        gaps=None,
    )
    out = StringIO()
    main.show_urls(args, out)
    mfindurls.assert_called_with(
        args.observatory,
        args.type,
        args.gpsstart,
        args.gpsend,
        match=args.match,
        urltype=args.url_type,
        on_gaps="ignore",
        ext=ext,
        host=args.server,
        api=args.api,
    )
    out.seek(0)
    assert list(map(str.rstrip, out.readlines())) == urls


@pytest.mark.parametrize(("fmt", "result"), [
    ("urls", GWF_OUTPUT_URLS),
    ("lal", GWF_OUTPUT_LAL_CACHE),
    ("names", GWF_OUTPUT_NAMES_ONLY),
    ("omega", GWF_OUTPUT_OMEGA_CACHE),
])
def test_postprocess_urls_format(fmt, result):
    """Test `postprocess_urls` with ``--format``."""
    # create namespace for parsing
    args = argparse.Namespace(
        type=None,
        format=fmt,
        names_only=False,
        frame_cache=False,
        gaps=None,
    )

    # run
    out = StringIO()
    if fmt == "omega":
        with pytest.deprecated_call(
            match="The omega cache format is deprecated",
        ):
            assert not main.postprocess_urls(GWF_URLS, args, out)
    else:
        assert not main.postprocess_urls(GWF_URLS, args, out)
    out.seek(0)
    assert out.read() == result


def test_postprocess_urls_sft():
    """Test `postprocess_urls` for SFTs."""
    args = argparse.Namespace(
        type="TEST_1800SFT",
        format=None,
        gaps=None,
    )
    out = StringIO()
    main.postprocess_urls(GWF_URLS, args, out)
    out.seek(0)
    assert out.read() == GWF_OUTPUT_URLS.replace(".gwf", ".sft")


def test_postprocess_urls_gaps(capsys):
    """Test `postprocess_urls()` with ``--gaps``."""
    args = argparse.Namespace(
        gpsstart=0,
        gpsend=10,
        type=None,
        format=None,
        gaps=True,
    )
    out = StringIO()
    assert main.postprocess_urls(URLS, args, out) == 1
    _, err = capsys.readouterr()
    segs = "\n".join(f"{seg[0]:d} {seg[1]:d}" for seg in GAPS)
    assert err == f"Missing segments:\n\n{segs}\n"

    args.gpsstart = 4
    args.gpsend = 7
    assert main.postprocess_urls(URLS, args, out) == 2


@mock.patch.dict(os.environ, {"GWDATAFIND_SERVER": "something"})
@pytest.mark.parametrize(("args", "patch"), [
    (["--ping"], "ping"),
    (["--show-observatories"], "show_observatories"),
    (["--show-types"], "show_types"),
    (["--show-times", "-o", "X", "-t", "test"], "show_times"),
    (["--latest", "-o", "X", "-t", "test"], "latest"),
    (["--filename", "X-test-0-1.gwf"], "filename"),
    (["-o", "X", "-t", "test", "-s", "0", "-e", "10"], "show_urls"),
])
def test_main(args, patch, tmp_path):
    """Test `main()`."""
    outfile = tmp_path / "out"

    with mock.patch(f"gwdatafind.__main__.{patch}") as mocked:
        main.main(args)
        assert mocked.call_count == 1
    # call again with output file
    args.extend(("--output-file", str(outfile)))
    with mock.patch(f"gwdatafind.__main__.{patch}") as mocked:
        main.main(args)
        assert mocked.call_count == 1
