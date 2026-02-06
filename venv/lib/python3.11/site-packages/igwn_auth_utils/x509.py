# Copyright (c) 2021-2025 Cardiff University
# Distributed under the terms of the BSD-3-Clause license

"""Utilities for discovering and handling X.509 credentials."""

import datetime
import os
import warnings
import sys
from functools import wraps
from pathlib import Path
from textwrap import indent

from cryptography.x509 import (
    Certificate,
    load_pem_x509_certificate,
)
from cryptography.hazmat.backends import default_backend

from .error import IgwnAuthError

X509_DEPRECATION_MESSAGE = """
Support for identity-based X.509 credentials for LIGO.ORG is being dropped.
Calls to this utility will stop working on/around 20 May 2025.

For details on this change please see

https://computing.docs.ligo.org/guide/compsoft/roadmap/LVK/x509_retirement/

If you have questions about this message, or its implications, please
consider opening an IGWN Computing Help Desk ticket:

https://git.ligo.org/computing/helpdesk/-/issues/new
""".strip()
X509_DEPRECATION_DOCSTRING_WARNING = f"""
.. warning::

{indent(X509_DEPRECATION_MESSAGE, '    ')}"""
if sys.version_info < (3, 13, 0):
    # older versions don't have https://github.com/python/cpython/issues/81283
    X509_DEPRECATION_DOCSTRING_WARNING = indent(
        X509_DEPRECATION_DOCSTRING_WARNING,
        "    ",
    )


def x509_deprecation(func):
    """Wrap ``func`` with a warning about X.509 support being dropped."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # warn about X.509 EOL
        warnings.warn(
            X509_DEPRECATION_MESSAGE,
            DeprecationWarning,
            stacklevel=2,
        )
        # call the function
        return func(*args, **kwargs)

    doclines = wrapper.__doc__.split("\n", 1)
    wrapper.__doc__ = "\n".join((
        doclines[0],
        X509_DEPRECATION_DOCSTRING_WARNING,
        *doclines[1:],
    ))

    return wrapper


def load_x509_certificate_file(file, backend=None):
    """Load a PEM-format X.509 certificate from a file, or file path.

    Parameters
    ----------
    file : `str`, `pathlib.Path`, `file`
        file object or path to read from

    backend : `module`, optional
        the `cryptography` backend to use

    Returns
    -------
    cert : `cryptography.x509.Certificate`
        the X.509 certificate
    """
    if isinstance(file, (str, bytes, os.PathLike)):
        with open(file, "rb") as fileobj:
            return load_x509_certificate_file(fileobj)
    if backend is None:  # cryptography < 3.1 requires a non-None backend
        backend = default_backend()
    return load_pem_x509_certificate(file.read(), backend=backend)


def validate_certificate(cert, timeleft=600):
    """Validate an X.509 certificate by checking it's expiry time.

    Parameters
    ----------
    cert : `cryptography.x509.Certificate`, `str`, `file`
        the certificate object or file (object or path) to validate

    timeleft : `float`, optional
        the minimum required time until expiry (seconds)

    Raises
    ------
    ValueError
        if the certificate has expired or is about to expire
    """
    # load a certificate from a file
    if not isinstance(cert, Certificate):
        cert = load_x509_certificate_file(cert)

    # then validate it
    if _timeleft(cert) < timeleft:
        raise ValueError(
            f"X.509 certificate has less than {timeleft} seconds remaining"
        )


def is_valid_certificate(cert, timeleft=600):
    """Return True if ``cert`` contains a valid X.509 certificate.

    Parameters
    ----------
    cert : `cryptography.x509.Certificate`, `str`, `file`
        the certificate object or file (object or path) to validate

    timeleft : `float`, optional
        the minimum required time until expiry (seconds)

    Returns
    -------
    isvalid : `bool`
        whether the certificate is valid
    """
    try:
        validate_certificate(cert, timeleft=timeleft)
    except (
        OSError,  # file doesn't exist or isn't readable
        ValueError,  # cannot load PEM certificate or expiry looming
    ):
        return False
    return True


def _timeleft(cert):
    """Return the time remaining (in seconds) for a ``cert``."""
    try:
        expiry = cert.not_valid_after_utc
    except AttributeError:
        # cryptography < 42
        expiry = cert.not_valid_after.astimezone(datetime.timezone.utc)
    now = datetime.datetime.now(datetime.timezone.utc)
    return (expiry - now).total_seconds()


def _default_cert_path(prefix="x509up_"):
    r"""Return the temporary path for a user's X509 certificate.

    Examples
    --------
    On Windows:

    >>> _default_cert_path()
    'C:\\Users\\user\\AppData\\Local\\Temp\\x509up_user'

    On Unix:

    >>> _default_cert_path()
    '/tmp/x509up_u1000'
    """
    if os.name == "nt":  # Windows
        tmpdir = Path(os.environ["SYSTEMROOT"]) / "Temp"
        user = os.getlogin()
    else:  # Unix
        tmpdir = "/tmp"  # noqa: S108
        user = "u{}".format(os.getuid())
    return Path(tmpdir) / "{}{}".format(prefix, user)


def _globus_cert_path():
    """Return the default paths for Globus 'grid' certificate files."""
    globusdir = Path.home() / ".globus"
    return (
        globusdir / "usercert.pem",
        globusdir / "userkey.pem",
    )


@x509_deprecation
def find_credentials(
    timeleft=600,
    on_error="warn",
):
    """Locate X509 certificate and (optionally) private key files.

    This function checks the following paths in order:

    - ``${X509_USER_CERT}`` and ``${X509_USER_KEY}``
    - ``${X509_USER_PROXY}``
    - ``/tmp/x509up_u${UID}``
    - ``~/.globus/usercert.pem`` and ``~/.globus/userkey.pem``

    Any located X.509 credential is validated using
    :func:`~igwn_auth_utils.find_x509_credentials`, with validation
    failures handled according to ``on_error``.

    Parameters
    ----------
    timeleft : `int`
        The minimum required time (in seconds) remaining until expiry
        for a certificate to be considered 'valid'

    on_error : `str`
        How to handle errors reading/validating an X.509 certificate file.
        One of:

        - ``"ignore"`` - do nothing and move on to the next candidate
        - ``"warn"`` - emit a warning and move on to the next candidate
        - ``"raise"`` - raise the exception immediately

    Returns
    -------
    cert : `str`
        the path of the certificate file that also contains the
        private key, **OR**

    cert, key : `str`
        the paths of the separate cert and private key files

    Raises
    ------
    ~igwn_auth_utils.IgwnAuthError
        if not certificate files can be found, or if the files found on
        disk cannot be validtted.

    See Also
    --------
    ~igwn_auth_utils.find_x509_credentials
        For details of the certificate validation.

    Examples
    --------
    If no environment variables are set, but a short-lived certificate has
    been generated in the default location:

    >>> find_credentials()
    '/tmp/x509up_u1000'

    If a long-lived (grid) certificate has been downloaded:

    >>> find_credentials()
    ('/home/me/.globus/usercert.pem', '/home/me/.globus/userkey.pem')
    """
    def _validate(cert, key):
        validate_certificate(cert, timeleft=timeleft)

        # check we can read the key file
        if key is not None:
            with open(key, "rb"):
                pass

    ignore = on_error == "ignore"
    warn = on_error == "warn"
    error = None

    for candidate in _find_credentials():
        # unpack cert, key pair or combined cert+key file
        try:
            cert, key = candidate
        except ValueError:
            cert = candidate[0]
            key = None
        # validate and return if valid, otherwise move on
        try:
            _validate(cert, key)
        except Exception as exc:
            error = error or exc  # store (first) error for later
            if ignore:
                continue
            msg = f"Failed to validate '{cert}': {type(exc).__name__}: {exc}"
            if warn:
                warnings.warn(msg)
                continue
            raise IgwnAuthError(msg) from exc  # stop here and raise

        return str(cert) if key is None else (str(cert), str(key))

    raise IgwnAuthError(
        "could not find an RFC-3820 compliant X.509 credential, "
        "please generate one and try again.",
    ) from error


def _find_credentials():
    """Yield all candidate X.509 credentials we can find."""
    # -- check environment variables
    # unlike the default paths below, here we don't pre-check that the
    # files actually exist; this allows the validation to fail and the
    # user to receive a warning or exception about it

    if "X509_USER_CERT" in os.environ and "X509_USER_KEY" in os.environ:
        yield os.environ['X509_USER_CERT'], os.environ['X509_USER_KEY']

    proxy = os.getenv("X509_USER_PROXY", None)
    if proxy is not None:
        yield proxy,

    # -- look up some default paths

    # 1: /tmp/x509up_u<uid> (cert = key)
    default = _default_cert_path()
    if default.exists():
        yield default,

    # 2: ~/.globus/user{cert,key}.pem
    try:
        cert, key = _globus_cert_path()
    except RuntimeError:  # pragma: no cover
        # no 'home'
        pass
    else:
        if cert.exists() and key.exists():
            yield cert, key
