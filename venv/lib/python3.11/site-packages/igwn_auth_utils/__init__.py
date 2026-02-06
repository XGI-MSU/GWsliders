# Copyright (c) 2021-2025 Cardiff University
# Distributed under the terms of the BSD-3-Clause license

"""Utilities to simplify using IGWN authorisation credentials.

This project is primarily aimed at discovering X.509 credentials and
SciTokens for use with HTTP(S) requests to IGWN-operated services.
"""

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"
__credits__ = "Duncan Brown, Leo Singer"
__license__ = "BSD-3-Clause"

from .error import IgwnAuthError
from .kerberos import kinit
from .requests import (
    get,
    request,
    HTTPSciTokenAuth,
    Session,
    SessionAuthMixin,
    SessionErrorMixin,
)
from .scitokens import (
    find_token as find_scitoken,
    get_scitoken,
    token_authorization_header as scitoken_authorization_header,
)
from .x509 import (
    find_credentials as find_x509_credentials,
)

try:  # parse version
    from ._version import version as __version__
except ModuleNotFoundError:  # development mode
    __version__ = 'dev'
