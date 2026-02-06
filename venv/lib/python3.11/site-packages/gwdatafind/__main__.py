# Copyright (C) 2017-2025 Cardiff University
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

"""Query a GWDataFind server for information."""

import argparse
import logging
import re
import sys

import igwn_segments as segments

from . import (
    __version__,
    api,
    ui,
)
from .io import Cache
from .utils import get_default_host

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"
__credits__ = "Scott Koranda, The LIGO Scientific Collaboration"


# -- command line parsing -----------------------------------------------------

class DataFindFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawDescriptionHelpFormatter,
):
    """Custom `argparse.Formatter` for GWDataFind."""


class DataFindArgumentParser(argparse.ArgumentParser):
    """Custom `~argparse.ArgumentParser` for GWDataFind.

    Mainly to handle the legacy mutually-exclusive optional arguments...
    """

    def __init__(self, *args, **kwargs):
        """Create a new `DataFindArgumentParser`."""
        kwargs.setdefault("formatter_class", DataFindFormatter)
        super().__init__(*args, **kwargs)
        self._optionals.title = "Optional arguments"

    def parse_args(self, *args, **kwargs):
        """Parse arguments with an extra sanity check."""
        args = super().parse_args(*args, **kwargs)
        args.show_urls = not any((args.ping, args.show_observatories,
                                  args.show_types, args.show_times,
                                  args.filename, args.latest))
        self.sanity_check(args)
        return args

    def sanity_check(self, namespace):
        """Sanity check parsed command line options.

        If any problems are found `argparse.ArgumentParser.error` is called,
        which in turn calls :func:`sys.exit`.

        Parameters
        ----------
        namespace : `argparse.Namespace`
            the output of the command-line parsing
        """
        if namespace.show_times and (
            not namespace.observatory
            or not namespace.type
        ):
            self.error("--observatory and --type must be given when using "
                       "--show-times.")
        if namespace.show_urls and not all(x is not None for x in (
                namespace.observatory,
                namespace.type,
                namespace.gpsstart,
                namespace.gpsend,
        )):
            self.error("--observatory, --type, --gps-start-time, and "
                       "--gps-end-time time all must be given when querying "
                       "for file URLs")
        if namespace.gaps and not namespace.show_urls:
            self.error("-g/--gaps only allowed when querying for file URLs")


def command_line():
    """Build an `~argparse.ArgumentParser` for the `gwdatafind` CLI."""
    try:
        defhost = get_default_host()
    except ValueError:
        defhost = None

    parser = DataFindArgumentParser(
        description=__doc__,
    )
    parser.man_short_description = __doc__.splitlines()[0].lower().rstrip(".")

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (give once for `INFO`, twice for `DEBUG`).",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=__version__,
        help="show version number and exit",
    )

    qargs = parser.add_argument_group(
        "Query types",
        "Select one of the following, if none are selected a "
        "query for frame URLS will be performed",
    )
    qtype = qargs.add_mutually_exclusive_group(required=False)
    parser._mutually_exclusive_groups.append(qtype)  # bug in argparse
    qtype.add_argument(
        "-p",
        "--ping",
        action="store_true",
        default=False,
        help="ping the DataFind server",
    )
    qtype.add_argument(
        "-w",
        "--show-observatories",
        action="store_true",
        default=False,
        help="list available observatories",
    )
    qtype.add_argument(
        "-y",
        "--show-types",
        action="store_true",
        default=False,
        help="list available file types",
    )
    qtype.add_argument(
        "-a",
        "--show-times",
        action="store_true",
        default=False,
        help="list available segments",
    )
    qtype.add_argument(
        "-f",
        "--filename",
        action="store",
        metavar="FILE",
        help="resolve URL(s) for a particular file name",
    )
    qtype.add_argument(
        "-T",
        "--latest",
        action="store_true",
        default=False,
        help="resolve URL(s) for the most recent file of the specified type",
    )

    dargs = parser.add_argument_group(
        "Data options",
        "Parameters for your query. "
        "Which options are required depends on the query type",
    )
    dargs.add_argument(
        "-o",
        "--observatory",
        metavar="OBS",
        help=(
            "observatory(ies) that generated frame file; "
            "use --show-observatories to see what is available."
        ),
    )
    dargs.add_argument(
        "-t",
        "--type",
        help="type of frame file, use --show-types to see what is available.",
    )
    dargs.add_argument(
        "-s",
        "--gps-start-time",
        type=int,
        dest="gpsstart",
        metavar="GPS",
        help="start of GPS time search",
    )
    dargs.add_argument(
        "-e",
        "--gps-end-time",
        type=int,
        dest="gpsend",
        metavar="GPS",
        help="end of GPS time search",
    )
    dargs.add_argument(
        "-x",
        "--extension",
        metavar="EXT",
        default=ui.DEFAULT_EXT,
        help="file extension for which to search",
    )

    sargs = parser.add_argument_group(
        "Connection options",
        "Authentication and connection options.",
    )
    sargs.add_argument(
        "-r",
        "--server",
        metavar="HOST",
        default=defhost,
        required=not defhost,
        help="hostname and optional port of server to query",
    )
    sargs.add_argument(
        "-P",
        "--no-proxy",
        action="store_true",
        help="attempt to authenticate without a grid proxy",
    )
    sargs.add_argument(
        "-A",
        "--api",
        default=api.DEFAULT_API,
        choices=api.APIS,
        help="API version to use",
    )

    oargs = parser.add_argument_group(
        "Output options",
        "Parameters for parsing and writing output.",
    )
    oform = oargs.add_mutually_exclusive_group()
    parser._mutually_exclusive_groups.append(oform)  # bug in argparse
    oform.add_argument(
        "-l",
        "--lal-cache",
        action="store_const",
        const="lal",
        default=False,
        dest="format",
        help="format output for use as a LAL cache file",
    )
    oform.add_argument(
        "-W",
        "--frame-cache",
        action="store_const",
        const="omega",
        default=False,
        dest="format",
        help="[DEPRECATED] format output for use as a frame cache file",
    )
    oform.add_argument(
        "-n",
        "--names-only",
        action="store_const",
        const="names",
        default=False,
        dest="format",
        help="display only the basename of each file",
    )
    oargs.add_argument(
        "-m",
        "--match",
        help="return only results that match a regular expression",
    )
    oargs.add_argument(
        "-u",
        "--url-type",
        default="file",
        help=(
            "return only URLs with a particular scheme or head "
            'such as "file" or "gsiftp"'
        ),
    )
    oargs.add_argument(
        "-g",
        "--gaps",
        action="store_true",
        help=(
            "check the returned list of URLs or paths to see "
            "if the files cover the requested interval; a "
            "return value of zero (0) indicates the interval "
            "is covered, a value of one (1) indicates at "
            "least one gap exists and the interval is not , "
            "covered and a value of (2) indicates that the "
            "entire interval is not covered; missing gaps are "
            "printed to stderr"
        ),
    )
    oargs.add_argument(
        "-O",
        "--output-file",
        metavar="PATH",
        help="path to output file, defaults to stdout",
    )

    return parser


# -- actions ------------------------------------------------------------------

def ping(args, out):
    """Worker for the --ping option.

    Parameters
    ----------
    args : `argparse.Namespace`
        the parsed command-line options.

    out : `file`
        the open file object to write to.

    Returns
    -------
    exitcode : `int` or `None`
        the return value of the action or `None` to indicate success.
    """
    resp = ui.ping(
        host=args.server,
        api=args.api,
    )
    if "version" in resp:
        msg = f"GWDataFind Server v{resp['version']} at {args.server} is alive"
    else:
        msg = f"LDRDataFindServer at {args.server} is alive"
    print(msg, file=out)


def show_observatories(args, out):
    """Worker for the --show-observatories option.

    Parameters
    ----------
    args : `argparse.Namespace`
        the parsed command-line options.

    out : `file`
        the open file object to write to.

    Returns
    -------
    exitcode : `int` or `None`
        the return value of the action or `None` to indicate success.
    """
    sitelist = ui.find_observatories(
        ext=args.extension,
        match=args.match,
        host=args.server,
        api=args.api,
    )
    print("\n".join(sitelist), file=out)


def show_types(args, out):
    """Worker for the --show-types option.

    Parameters
    ----------
    args : `argparse.Namespace`
        the parsed command-line options.

    out : `file`
        the open file object to write to.

    Returns
    -------
    exitcode : `int` or `None`
        the return value of the action or `None` to indicate success.
    """
    typelist = ui.find_types(
        site=args.observatory,
        ext=args.extension,
        match=args.match,
        host=args.server,
        api=args.api,
    )
    print("\n".join(typelist), file=out)


def show_times(args, out):
    """Worker for the --show-times option.

    Parameters
    ----------
    args : `argparse.Namespace`
        the parsed command-line options.

    out : `file`
        the open file object to write to.

    Returns
    -------
    exitcode : `int` or `None`
        the return value of the action or `None` to indicate success.
    """
    seglist = ui.find_times(
        site=args.observatory,
        frametype=args.type,
        gpsstart=args.gpsstart,
        gpsend=args.gpsend,
        ext=args.extension,
        host=args.server,
        api=args.api,
    )
    print("# seg\tstart     \tstop      \tduration", file=out)
    for i, seg in enumerate(seglist):
        print(
            f"{i}\t{seg[0]:10}\t{seg[1]:10}\t{abs(seg)}",
            file=out,
        )


def latest(args, out):
    """Worker for the --latest option.

    Parameters
    ----------
    args : `argparse.Namespace`
        the parsed command-line options.

    out : `file`
        the open file object to write to.

    Returns
    -------
    exitcode : `int` or `None`
        the return value of the action or `None` to indicate success.
    """
    urls = ui.find_latest(
        args.observatory,
        args.type,
        ext=args.extension,
        urltype=args.url_type,
        on_missing="warn",
        host=args.server,
        api=args.api,
    )
    return postprocess_urls(urls, args, out)


def filename(args, out):
    """Worker for the --filename option.

    Parameters
    ----------
    args : `argparse.Namespace`
        the parsed command-line options.

    out : `file`
        the open file object to write to.

    Returns
    -------
    exitcode : `int` or `None`
        the return value of the action or `None` to indicate success.
    """
    urls = ui.find_url(
        args.filename,
        urltype=args.url_type,
        on_missing="warn",
        host=args.server,
        api=args.api,
    )
    return postprocess_urls(urls, args, out)


def show_urls(args, out):
    """Worker for the default (show-urls) option.

    Parameters
    ----------
    args : `argparse.Namespace`
        the parsed command-line options.

    out : `file`
        the open file object to write to.

    Returns
    -------
    exitcode : `int` or `None`
        the return value of the action or `None` to indicate success.
    """
    urls = ui.find_urls(
        args.observatory,
        args.type,
        args.gpsstart,
        args.gpsend,
        ext=args.extension,
        match=args.match,
        urltype=args.url_type,
        on_gaps="ignore",
        host=args.server,
        api=args.api,
    )
    return postprocess_urls(urls, args, out)


def postprocess_urls(urls, args, out):
    """Post-process a list of URLs produced from a DataFind query.

    This function checks for gaps in the file coverage, prints the URLs
    in the requested format, then prints gaps to stderr if requested.
    """
    # if searching for SFTs replace '.gwf' file suffix with '.sft'
    if re.search(r"_\d+SFT(\Z|_)", str(args.type)):
        gwfreg = re.compile(r"\.gwf\Z")
        for i, url in enumerate(urls):
            urls[i] = gwfreg.sub(".sft", url)

    cache = Cache(urls)

    # print the cache in the requested format
    cache.write(out, args.format or "urls")

    # check for gaps
    if args.gaps:
        span = segments.segment(args.gpsstart, args.gpsend)
        seglist = segments.segmentlist(e.segment for e in cache).coalesce()
        missing = (segments.segmentlist([span]) - seglist).coalesce()
        if missing:
            print("Missing segments:\n", file=sys.stderr)
            for seg in missing:
                print(f"{seg[0]:d} {seg[1]:d}", file=sys.stderr)
            if span in missing:
                return 2
            return 1


# -- CLI ----------------------------------------------------------------------

def main(args=None):
    """Run the thing."""
    # parse command line
    parser = command_line()
    opts = parser.parse_args(args=args)

    # enable rich logging
    logging.basicConfig(
        level=max(3 - opts.verbose, 0) * 10,
        format="%(asctime)s:%(name)s[%(process)d]:%(levelname)s:%(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    # open output
    if opts.output_file:
        out = open(opts.output_file, "w")
    else:
        out = sys.stdout

    try:
        # run query
        if opts.ping:
            return ping(opts, out)
        if opts.show_observatories:
            return show_observatories(opts, out)
        if opts.show_types:
            return show_types(opts, out)
        if opts.show_times:
            return show_times(opts, out)
        if opts.latest:
            return latest(opts, out)
        if opts.filename:
            return filename(opts, out)
        return show_urls(opts, out)
    finally:
        # close output file if we opened it
        if opts.output_file:
            out.close()


if __name__ == "__main__":  # pragma: no-cover
    sys.exit(main())
