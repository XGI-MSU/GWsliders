# Copyright (c) 2025 Cardiff University
# Distributed under the terms of the BSD-3-Clause license

"""Tests for :mod:`igwn_auth_utils.kerberos`."""

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

import os
from unittest import mock

import pytest

from .. import kerberos

# with pytest >= 8.2.0 this can be replaced with
# pytest.importorskip("gssapi", exc_type=(ImportError, OSError))
try:
    import gssapi
except (
    ImportError,  # module not installed
    OSError,  # Kerberos implementation not available (Windows)
) as exc:
    pytest.skip(
       f"could not import 'gssapi': {exc}",
       allow_module_level=True,
    )


def kerberos_name(name):
    """Format ``name`` into a `gssapi.Name`."""
    import gssapi
    return gssapi.Name(
        base=name,
        name_type=gssapi.NameType.kerberos_principal,
    )


@pytest.fixture
def keytab(tmp_path):
    """Create a temporary empty keytab file with 400 permissions."""
    keytab = tmp_path / "keytab"
    keytab.touch()
    keytab.chmod(0o400)
    return keytab


@mock.patch("gssapi.Credentials")
def test_kinit_keytab(creds, keytab):
    """Test `kinit()`."""
    ccache = keytab.parent / "ccache"

    # test keytab kwarg
    kerberos.kinit(
        "rainer.weiss@LIGO.ORG",
        keytab=keytab,
        ccache=ccache,
    )
    creds.assert_called_once_with(
        name=kerberos_name("rainer.weiss@LIGO.ORG"),
        store={
            "client_keytab": str(keytab),
            "ccache": str(ccache),
        },
        usage="initiate",
    )


@mock.patch.dict("os.environ")
@mock.patch("gssapi.Credentials")
def test_kinit_keytab_env(creds, keytab):
    """Test `kinit()` can handle keytabs from the environment."""
    os.environ["KRB5_KTNAME"] = str(keytab)

    kerberos.kinit("rainer.weiss@LIGO.ORG")
    creds.assert_called_with(
        name=kerberos_name("rainer.weiss@LIGO.ORG"),
        store={
            "client_keytab": str(keytab),
        },
        usage="initiate",
    )


@pytest.mark.parametrize(("permissions", "ok"), [
    (0o400, True),  # best
    (0o700, True),  # acceptable
    (0o644, False),  # default, not ok
    (0o440, False),  # group read, not ok
    (0o404, False),  # other read, not ok
])
def test_check_keytab(keytab, permissions, ok):
    """Test `_check_keytab` with various permissions."""
    keytab.chmod(permissions)
    try:
        kerberos._check_keytab(keytab)
    except OSError:
        perm_check = False
    else:
        perm_check = True
    assert perm_check is ok
