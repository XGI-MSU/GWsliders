# Copyright (c) 2025 Cardiff University
# SPDX-License-Identifier: BSD-3-Clause

"""Utility module to initialise Kerberos ticket-granting tickets.

This module provides a lazy-mans python version of the 'kinit'
command-line tool using the python-gssapi library.

See the documentation of the `kinit` function for example usage.
"""

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

import logging
import os
import stat
from pathlib import Path
from unittest import mock

__all__ = [
    "kinit",
]

log = logging.getLogger(__name__)

# Invalid Kerberos keytab permissions: anything giving group or other access is bad
BAD_KEYTAB_PERMISSIONS = stat.S_IRWXG | stat.S_IRWXO


def _check_keytab(keytab):
    """Check the Kerberos keytab.

    This just checks that the keytab has appropriate permissions.

    Raises
    ------
    OSError
        If the permissions on the keytab allow any access to 'group'
        or 'other' users.
    """
    mode = Path(keytab).stat().st_mode
    if mode & BAD_KEYTAB_PERMISSIONS:
        msg = (
            f"Permissions on '{keytab}' are incorrect; "
            "please restrict access to the file owner only.\n\n"
            f"Run `chown {keytab} 400"
        )
        raise OSError(msg)


def _keytab_principal(
    keytab,
):
    """Return the principal assocated with a Kerberos keytab file."""
    import gssapi
    with mock.patch.dict("os.environ", {"KRB5_KTNAME": str(keytab)}):
        return gssapi.Credentials(usage="accept").name


def _canonical_principal(principal):
    """Canonicalise the principal name."""
    import gssapi

    principal = gssapi.Name(
        base=principal,
        name_type=gssapi.NameType.kerberos_principal,
    )
    try:
        # applies default realm if not given
        return principal.canonicalize(
            gssapi.MechType.kerberos,
        )
    except gssapi.exceptions.GSSError as exc:
        msg = (
            "failed to canonicalize Kerberos principal name, "
            "please specify principal as <name@REALM>."
        )
        raise ValueError(msg) from exc


def _parse_options(
    principal,
    keytab,
):
    if keytab is None:
        keytab = os.getenv("KRB5_KTNAME")
    if keytab is None:
        msg = "keytab not passed or found via KRB5_KTNAME environment variable"
        raise ValueError(msg)

    if principal is None:
        principal = _keytab_principal(keytab)

    return _canonical_principal(principal), keytab


def kinit(
    principal=None,
    keytab=None,
    ccache=None,
):
    """Initialise a Kerberos ticket-granting ticket (TGT).

    The method works in the same way as the ``kinit`` command-line tool,
    with the caveat that it only works with Kerberos keytab files, and does
    not support interactive input of principal passwords.

    Parameters
    ----------
    principal : `str`, optional
        Principal name for Kerberos credential.
        If not given it will be taken from the ``keytab``.
        If ``principal`` is not specified in the form ``name@REALM``
        the default realm REALM will be applied, see ``man krb5.conf(5)``.

    keytab : `str`, optional
        Path to keytab file.
        Default taken from ``KRB5_KTNAME`` environment variable.
        This option is required to be not `None`.

    ccache : `str`, optional
        Path to Kerberos credentials cache.

    Examples
    --------
    When ``KRB5_KTNAME`` environment variable is set, this function
    can operate with no arguments:

    >>> kinit()

    If the Kerberos config (``krb5.conf``) has a default realm configured,
    the ``principal`` can be specified without that component:

    >>> kinit("albert.einstein")
    """
    # import gssapi here so that the top-level module doesn't force users to
    # have a fully-configured MIT Kerberos stack that they might not use.
    import gssapi

    # canonicalise the principal and keytab options
    principal, keytab = _parse_options(principal, keytab)

    # validate the permissions on the keytab
    _check_keytab(keytab)
    keytab = str(keytab)

    # construct the name
    name = gssapi.Name(
       base=principal,
       name_type=gssapi.NameType.kerberos_principal,
    )

    log.debug("Acquiring Kerberos credential for %s", name)
    store = {
        "client_keytab": keytab,
    }
    if ccache:
        store["ccache"] = str(ccache)
        log.debug("Using ccache = '%s'", ccache)
    with mock.patch.dict("os.environ", {"KRB5_KTNAME": keytab}):
        creds = gssapi.Credentials(
            name=name,
            store=store,
            usage="initiate",
        )
    creds.inquire()
    log.debug("Credential acquired, timeleft: %d", creds.lifetime)
    return creds
