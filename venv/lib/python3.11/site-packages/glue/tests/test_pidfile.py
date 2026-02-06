#!/usr/bin/env python

import os.path
import pytest
import tempfile

from glue import pidfile


class TestPidfile:

    def test_get_lock(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lockfile = os.path.join(tmpdir, "lock.pid")
            pidfile.get_lock(lockfile)
            pidfile.confirm_lock(lockfile)

    def test_duplicate_lock(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lockfile = os.path.join(tmpdir, "lock.pid")
            pidfile.get_lock(lockfile)
            pidfile.confirm_lock(lockfile)
            # cannot get the same lock twice
            with pytest.raises(
                RuntimeError,
                match=r"pidfile .* contains pid \([0-9]+\) of a running process",
            ):
                pidfile.get_lock(lockfile)
