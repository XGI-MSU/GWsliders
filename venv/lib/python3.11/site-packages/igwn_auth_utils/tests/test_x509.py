# Copyright (c) 2021-2025 Cardiff University
# Distributed under the terms of the BSD-3-Clause license

"""Tests for :mod:`igwn_auth_utils.x509`."""

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

import datetime
import os
from pathlib import Path
from unittest import mock

try:
    from contextlib import nullcontext
except ImportError:  # Python < 3.7
    from contextlib import contextmanager

    @contextmanager
    def nullcontext(enter_result=None):
        yield enter_result

import pytest
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import (
    hashes,
    serialization,
)
from cryptography.x509.oid import NameOID
from packaging.version import Version

from .. import x509 as igwn_x509
from ..error import IgwnAuthError

PYTEST_LT_8 = Version(pytest.__version__) < Version("8.0.0")

x509_warning_ctx = pytest.warns(
    DeprecationWarning,
    match="Support for identity-based X.509 credentials",
)


# -- fixtures ---------------

@pytest.fixture
def x509cert(private_key, public_key):
    name = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "test"),
    ])
    try:
        now = datetime.datetime.now(datetime.UTC)
    except AttributeError:  # python < 3.11
        now = datetime.datetime.utcnow()
    return x509.CertificateBuilder(
        issuer_name=name,
        subject_name=name,
        public_key=public_key,
        serial_number=1000,
        not_valid_before=now,
        not_valid_after=now + datetime.timedelta(seconds=86400),
    ).sign(private_key, hashes.SHA256(), backend=default_backend())


def _write_x509(cert, path):
    with open(path, "wb") as file:
        file.write(cert.public_bytes(
            serialization.Encoding.PEM,
        ))


@pytest.fixture
def x509cert_path(x509cert, tmp_path):
    cert_path = tmp_path / "x509.pem"
    _write_x509(x509cert, cert_path)
    return cert_path


# -- tests ------------------

@mock.patch.dict("os.environ")
@mock.patch(
    "os.getlogin" if os.name == "nt" else "os.getuid",
    mock.MagicMock(return_value=123),
)
def test_default_cert_path():
    if os.name == "nt":
        os.environ["SYSTEMROOT"] = r"C:\WINDOWS"
        expected = r"C:\WINDOWS\Temp\x509up_123"
    else:
        expected = r"/tmp/x509up_u123"  # noqa: S108
    assert igwn_x509._default_cert_path() == Path(expected)


def test_validate_certificate(x509cert):
    igwn_x509.validate_certificate(x509cert)


def test_validate_certificate_path(x509cert_path):
    igwn_x509.validate_certificate(x509cert_path)


def test_validate_certificate_expiry_error(x509cert):
    with pytest.raises(
        ValueError,
        match="X.509 certificate has less than 10000000000 seconds remaining",
    ):
        igwn_x509.validate_certificate(x509cert, timeleft=int(1e10))


def test_is_valid_certificate(x509cert_path):
    assert igwn_x509.is_valid_certificate(x509cert_path)


def test_is_valid_certificate_false(tmp_path):
    assert not igwn_x509.is_valid_certificate(tmp_path / "does-not-exist")


@mock.patch.dict("os.environ")
def test_find_credentials_x509usercertkey(x509cert_path, public_pem_path):
    """Test that `find_credentials()` returns the X509_USER_{CERT,KEY} pair."""
    # configure the environment to return (cert, key)
    x509cert_filename = str(x509cert_path)
    x509key_filename = str(public_pem_path)
    os.environ["X509_USER_CERT"] = x509cert_filename
    os.environ["X509_USER_KEY"] = x509key_filename

    # check that find_credentials() returns the (cert, key) pair
    with x509_warning_ctx:
        assert igwn_x509.find_credentials() == (
            x509cert_filename,
            x509key_filename,
        )


@mock.patch.dict("os.environ")
def test_find_credentials_x509userproxy(x509cert_path):
    """Test that `find_credentials()` returns the ``X509_USER_PROXY`` if set.

    When ``X509_USER_{CERT,KEY}`` are not set
    """
    # remove CERT,KEY so that PROXY can win
    os.environ.pop("X509_USER_CERT", None)
    os.environ.pop("X509_USER_KEY", None)
    # set the PROXY variable
    x509cert_filename = str(x509cert_path)
    os.environ["X509_USER_PROXY"] = x509cert_filename
    # make sure it gets found
    with x509_warning_ctx:
        assert igwn_x509.find_credentials() == x509cert_filename


@mock.patch.dict("os.environ", clear=True)
@mock.patch("igwn_auth_utils.x509._default_cert_path")
def test_find_credentials_default(_default_cert_path, x509cert_path):
    """Test that `find_credentials()` returns the default path.

    When none of the X509_USER variable are set.
    """
    _default_cert_path.return_value = x509cert_path
    with x509_warning_ctx:
        assert igwn_x509.find_credentials() == str(x509cert_path)


@mock.patch.dict(
    "os.environ",
)
@mock.patch(
    "igwn_auth_utils.x509.validate_certificate",
    return_value=True,
)
@mock.patch(
    "pathlib.Path.exists",
    side_effect=(
        False,  # default path
        True,  # usercert.pem
        True,  # userkey.pem
    ),
)
@mock.patch("builtins.open", mock.mock_open())
def test_find_credentials_globus(mock_exists, mock_valid):
    """Test that .globus files are returned if all else fails."""
    # clear X509 variables out of the environment
    for suffix in ("PROXY", "CERT", "KEY"):
        os.environ.pop(f"X509_USER_{suffix}", None)

    # check that .globus is found
    globusdir = Path.home() / ".globus"
    with x509_warning_ctx:
        assert igwn_x509.find_credentials(on_error="raise") == (
        str(globusdir / "usercert.pem"),
        str(globusdir / "userkey.pem"),
    )


@mock.patch.dict("os.environ")
@mock.patch(
    "igwn_auth_utils.x509.validate_certificate",
    side_effect=ValueError,
)
def test_find_credentials_error(_):
    """Test that a failure in discovering X.509 creds raises the right error."""
    # clear X509 variables out of the environment
    for suffix in ("PROXY", "CERT", "KEY"):
        os.environ.pop(f"X509_USER_{suffix}", None)

    # check that we can't find any credentials
    with x509_warning_ctx, pytest.raises(
        IgwnAuthError,
        match="could not find an RFC-3820 compliant X.509 credential",
    ):
        igwn_x509.find_credentials(on_error="ignore")


@mock.patch.dict("os.environ")
@pytest.mark.parametrize(("on_error", "ctx"), [
    # no warnings, no errors
    ("ignore", nullcontext()),
    # a warning about validation
    ("warn", pytest.warns(
        UserWarning,
        match="^Failed to validate",
    )),
    # an exception about validation
    ("raise", pytest.raises(
        IgwnAuthError,
        match="^Failed to validate",
    )),
])
def test_find_credentials_on_error(
    on_error,
    ctx,
    x509cert_path,
    tmp_path,
):
    """Test that `find_credentials` uses ``on_error`` correctly."""
    # set cert and key to empty files that fail certificate validation
    empty = tmp_path / "blah"
    empty.touch()
    os.environ["X509_USER_CERT"] = os.environ["X509_USER_KEY"] = str(empty)

    # set the PROXY variable to a valid X.509 credential
    x509cert_filename = str(x509cert_path)
    os.environ["X509_USER_PROXY"] = x509cert_filename

    if PYTEST_LT_8 and on_error == "warn":
        # pytest < 8 doesn't handle stacking warn context managers
        _x509_warning_ctx = nullcontext()
    else:
        _x509_warning_ctx = x509_warning_ctx

    # attempt to find the cred
    with _x509_warning_ctx, ctx:
        cred = igwn_x509.find_credentials(on_error=on_error)

    # check that when we don't raise an exception the result is still correct
    if on_error in ("warn", "ignore"):
        assert cred == x509cert_filename
