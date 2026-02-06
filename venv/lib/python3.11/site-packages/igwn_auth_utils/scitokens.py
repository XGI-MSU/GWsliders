# Copyright (c) 2021-2025 Cardiff University
# Distributed under the terms of the BSD-3-Clause license

"""Utility functions for discovering valid scitokens."""

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

import contextlib
import logging
import os
import sys
import warnings
from pathlib import Path
from urllib.parse import urlparse

from jwt import (
    InvalidAudienceError,
    InvalidTokenError,
)
from scitokens import (
    Enforcer as _Enforcer,
    SciToken,
)
from scitokens.utils.errors import SciTokensException
from scitokens.scitokens import InvalidAuthorizationResource

from .error import IgwnAuthError

try:
    from shlex import join as shlex_join
except ImportError:  # python < 3.8
    import shlex

    def shlex_join(split):
        """Backport of `shlex.join` from Python 3.8."""
        return " ".join(map(shlex.quote, split))

log = logging.getLogger(__name__)

TOKEN_ERROR = (
    InvalidAudienceError,
    InvalidTokenError,
    SciTokensException,
)

WINDOWS = os.name == "nt"


# -- utilities --------------

class Enforcer(_Enforcer):
    """Custom `scitokens.Enforcer for IGWN Auth Utils`."""

    def __init__(self, *args, timeleft=0, **kwargs):
        super().__init__(*args, **kwargs)
        self._timeleft = timeleft
        self.add_validator("exp", self._validate_timeleft)

    def _validate_iss(self, value):
        if isinstance(self._issuer, (str, bytes)):
            return super()._validate_iss(value)
        return value in self._issuer

    def _validate_timeleft(self, value):
        exp = float(value)
        return exp >= self._now + self._timeleft


def is_valid_token(
    token,
    audience,
    scope,
    issuer=None,
    timeleft=60,
    warn=False,
):
    """Test whether a ``token`` is valid according to the given claims.

    Parameters
    ----------
    token : `scitokens.SciToken`, `str`
        The token object, or serialisation, to test

    audience : `str`, `list` or `str`
        The audience(s) to accept.

    scope : `str`, `list`
        One or more scopes to enforce.

    timeleft : `float`
        The amount of time remaining (in seconds, from the `exp` claim)
        to require.

    issuer : `str`, `list` of `str`
        The value of the `iss` claim to enforce.
        If ``issuer`` is given as a list (or other non-stringy container),
        the token will be required to match any of the entries.

    warn : `bool`
        If `True`, emit a warning when a token fails the enforcer test,
        useful in debugging bad tokens.

    Returns
    -------
    valid : `bool`
        `True` if the input ``token`` matches the required claims,
        otherwise `False`.
    """
    # if given a serialised token, deserialise it now
    if isinstance(token, (str, bytes)):
        try:
            token = SciToken.deserialize(token)
        except (InvalidTokenError, SciTokensException):
            return False

    # allow not specifying a required issuer
    if issuer is None:  # borrow the issuer from the token itself
        issuer = token["iss"]

    # if scope wasn't given, borrow one from the token to pass validation
    if scope is None:
        scope = token["scope"].split(" ", 1)[:1]

    # construct the issuer
    enforcer = Enforcer(
        issuer,
        audience=audience,
        timeleft=timeleft,
    )

    # iterate over given scopes and test all of them
    if isinstance(scope, str):
        scope = scope.split(" ")
    for scp in scope:
        # parse scope as scheme:path
        try:
            authz, path = scp.split(":", 1)
        except ValueError:
            authz = scp
            path = None

        # test
        try:
            res = enforcer.test(token, authz, path=path)
        except InvalidAuthorizationResource as exc:
            # bad scope in the token, is invalid
            res = False
            msg = f"{type(exc).__name__}: {exc}"
        else:
            msg = enforcer.last_failure
        if not res:
            if warn:
                warnings.warn(msg)
            return False

    return True


def target_audience(url, include_any=True):
    """Return the expected ``aud`` claim to authorize a request to ``url``.

    Parameters
    ----------
    url : `str`
        The URL that will be requested.

    include_any : `bool`, optional
        If `True`, include ``"ANY"`` in the return list of
        audiences, otherwise, don't.

    Returns
    -------
    audiences : `list` of `str`
        A `list` of audience values (`str`), either of length 1
        if ``include_any=False``, otherwise of length 2.

    Examples
    --------
    >>> default_audience(
    ...     "https://datafind.ligo.org:443/LDR/services/data/v1/gwf.json",
    ...     include_any=True,
    ... )
    ["https://datafind.ligo.org", "ANY"]
    >>> default_audience(
    ...     "segments.ligo.org",
    ...     include_any=False,
    ... )
    ["https://segments.ligo.org"]

    Hostnames given without a URL scheme are presumed to be HTTPS:

    >>> default_audience("datafind.ligo.org")
    ["https://datafind.ligo.org"]
    """
    if "//" not in url:  # always match a hostname, not a path
        url = f"//{url}"
    parsed = urlparse(url, scheme="https")
    aud = [f"{parsed.scheme}://{parsed.hostname}"]
    if include_any:
        aud.append("ANY")
    return aud


def token_authorization_header(token, scheme="Bearer"):
    """Format an in-memory token for use in an HTTP Authorization Header.

    Parameters
    ----------
    token : `scitokens.SciToken`
        the token to format

    scheme : `str` optional
        the Authorization scheme to use

    Returns
    -------
    header_str : `str`
        formatted content for an `Authorization` header

    Notes
    -----
    See `RFC-6750 <https://datatracker.ietf.org/doc/html/rfc6750>`__
    for details on the ``Bearer`` Authorization token standard.
    """
    return "{} {}".format(
        scheme,
        token._serialized_token or token.serialize().decode("utf-8"),
    )


# -- I/O --------------------

def deserialize_token(raw, **kwargs):
    """Deserialize a token.

    Parameters
    ----------
    raw : `str`
        the raw serialised token content to deserialise

    kwargs
        all keyword arguments are passed on to
        :meth:`scitokens.SciToken.deserialize`

    Returns
    -------
    token : `scitokens.SciToken`
        the deserialised token

    See Also
    --------
    scitokens.SciToken.deserialize
        The underlying deserialisation implementation.

    load_token_file
        A convenient wrapper for loading a
        `~scitokens.SciToken` from a file.

    Examples
    --------
    To load a token from a file:

    >>> with open("scitoken.use") as file:
    ...     token = deserialize_token(file)
    """
    return SciToken.deserialize(raw.strip(), **kwargs)


def load_token_file(path, **kwargs):
    """Load a SciToken from a file path.

    Parameters
    ----------
    path : `str`
        the path to the scitokens file

    kwargs
        all keyword arguments are passed on to :func:`deserialize_token`

    Returns
    -------
    token : `scitokens.SciToken`
        the deserialised token

    Examples
    --------
    To load a token and validate a specific audience:

    >>> load_token('mytoken', audience="my.service.org")

    See Also
    --------
    scitokens.SciToken.deserialize
        for details of the deserialisation, and any valid keyword arguments
    """
    with open(path, "r") as fobj:
        return deserialize_token(fobj.read(), **kwargs)


# -- discovery --------------

def find_token(
    audience,
    scope,
    issuer=None,
    timeleft=60,
    skip_errors=True,
    warn=False,
    **kwargs,
):
    """Find and load a `SciToken` for the given ``audience`` and ``scope``.

    Parameters
    ----------
    audience : `str`
        the required audience (``aud``).

    scope : `str`
        the required scope (``scope``).

    issuer : `str`
        the value of the `iss` claim to enforce.

    timeleft : `int`
        minimum required time left until expiry (in seconds)
        for a token to be considered 'valid'

    skip_errors : `bool`, optional
        skip over errors encoutered when attempting to deserialise
        discovered tokens; this may be useful to skip over invalid
        or expired tokens that exist, for example, which is why it
        is the default behaviour.

    warn : `bool`
        emit a warning when a token fails to deserialize, or fails
        validation.

    kwargs
        all keyword arguments are passed on to
        :meth:`scitokens.SciToken.deserialize`

    Returns
    -------
    token : `scitokens.SciToken`
        the first token that matches the requirements

    Raises
    ------
    ~igwn_auth_utils.IgwnAuthError
        if no valid token can be found

    See Also
    --------
    scitokens.SciToken.deserialize
        for details of the deserialisation, and any valid keyword arguments
    """
    # preserve error from parsing tokens
    error = None

    # iterate over all of the tokens we can find for this audience
    for token in _find_tokens(audience=audience, **kwargs):
        # parsing a token yielded an exception, handle it here:
        if isinstance(token, Exception):
            error = error or token  # record (first) error for later
            if warn:  # emit a warning
                warnings.warn(f"{type(error).__name__}: {error}")
            if skip_errors:
                continue  # move on
            raise IgwnAuthError(str(error)) from error  # stop here and raise

        # if this token is valid, stop here and return it
        if is_valid_token(
            token,
            audience,
            scope,
            issuer=issuer,
            timeleft=timeleft,
            warn=warn,
        ):
            return token

    # if we didn't find any valid tokens:
    raise IgwnAuthError(
        "could not find a valid SciToken, "
        "please verify the audience and scope, "
        "or generate a new token and try again",
    ) from error


def _find_tokens(**deserialize_kwargs):
    """Yield all tokens that we can find.

    This function will `yield` exceptions that are raised when
    attempting to parse a token that was actually found, so that
    they can be handled by the caller.
    """
    def _token_or_exception(func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TOKEN_ERROR as exc:
            return exc

    # read token directly from 'SCITOKEN{_FILE}' variable
    for envvar, loader in (
        ('SCITOKEN', deserialize_token),
        ('SCITOKEN_FILE', load_token_file),
    ):
        if envvar in os.environ:
            yield _token_or_exception(
                loader,
                os.environ[envvar],
                **deserialize_kwargs,
            )

    # try and find a token from HTCondor
    for tokenfile in _find_condor_creds_token_paths():
        yield _token_or_exception(
            load_token_file,
            tokenfile,
            **deserialize_kwargs,
        )

    try:
        yield _token_or_exception(SciToken.discover, **deserialize_kwargs)
    except OSError:  # no token
        pass  # try something else
    except AttributeError as exc:
        # windows doesn't have geteuid, that's ok, otherwise panic
        if not WINDOWS or "geteuid" not in str(exc):
            raise


def _find_condor_creds_token_paths():
    """Find all token files in the condor creds directory."""
    try:
        _condor_creds_dir = Path(os.environ["_CONDOR_CREDS"])
    except KeyError:
        return
    try:
        for f in _condor_creds_dir.iterdir():
            if f.suffix == ".use":
                yield f
    except FileNotFoundError:   # creds dir doesn't exist
        return


# -- token acquisition ---------------

def _format_argv(**kwargs):
    """Format arguments for ``htgettoken``."""
    args = []
    for key, value in kwargs.items():
        arg = f"--{key}"
        if value is False:  # disabled
            continue
        if value in (True, None):
            args.append(arg)
        else:
            args.extend((arg, str(value)))
    return args


def default_bearer_token_file(prefix="bt_"):
    """Return the default location for a bearer token.

    According to the WLCG Bearer Token Discovery protocol.
    """
    with contextlib.suppress(KeyError):
        return os.environ["BEARER_TOKEN_FILE"]
    if WINDOWS:
        tokendir = Path(os.environ["SYSTEMROOT"]) / "Temp"
        user = os.getlogin()
    else:
        tokendir = Path(os.getenv("XDG_RUNTIME_DIR", "/tmp"))  # noqa: S108
        user = f"u{os.getuid()}"
    return str(tokendir / f"{prefix}{user}")


def get_scitoken(
    *args,
    outfile=None,
    minsecs=60,
    quiet=True,
    **kwargs,
):
    """Get a new SciToken using |htgettoken|_ and return its file location.

    Parameters
    ----------
    args
        All positional arguments are passed as arguments to
        `htgettoken.main`.

    outfile : `str`, optional
        The path in which to serialize the new `SciToken`.
        Default given by :func:`default_bearer_token_file`.

    minsecs : `float`, optional
        The minimum remaining lifetime to reuse an existing bearer token.

    quiet : `bool`, optional
        If `True`, supress output from `htgettoken`.

    kwargs
        All ``key: value`` keyword arguments (including ``minsecs`` and
        ``quiet``) are passed as ``--key=value`` options to
        `htgettoken.main`. Keywords with the value `True` are passed simply
        as ``--key``, while those with the value `False` are omitted.

    Returns
    -------
    tokenfile: `str`
        The path to the bearer token file acquired by `htgettoken`.

    See Also
    --------
    igwn_auth_utils.scitokens.default_bearer_token_file
        For information on the default bearer token path.
    """
    import htgettoken

    if not sys.stdout.isatty():
        # don't prompt if we can't get a response
        kwargs.setdefault("nooidc", True)

    # parse output file if given
    if outfile is None:
        outfile = default_bearer_token_file()

    # get token in a temporary directory
    argv = list(args) + _format_argv(
        outfile=outfile,
        minsecs=minsecs,
        quiet=quiet,
        **kwargs,
    )
    log.debug("Acquiring SciToken with htgettoken")
    log.debug("$ htgettoken %s", shlex_join(argv))
    try:
        htgettoken.main(argv)
    except SystemExit as exc:  # bad args
        msg = "htgettoken failed, see full traceback for details"
        raise RuntimeError(msg) from exc
    log.debug("SciToken written to %s", outfile)
    return outfile
