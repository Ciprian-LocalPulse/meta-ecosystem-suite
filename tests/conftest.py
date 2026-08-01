"""Shared pytest fixtures.

`no_real_network` runs for every test automatically and asserts that
nothing escapes to a live socket. Combined with respx-mocked routes in
the individual test modules, this guarantees the suite is fully
offline and deterministic — it will fail loudly (instead of silently
depending on internet access, or being skipped) if a future change
reintroduces an un-mocked network call.
"""

import pytest
import respx


@pytest.fixture(autouse=True)
def no_real_network():
    """Route all HTTPX traffic through respx by default.

    Individual tests register their own mocked routes with
    `@respx.mock`; this fixture is a safety net for any test that
    forgets to. Any request that doesn't match a registered route
    raises `respx.errors.AllMockedAssertionError` instead of hitting
    the network.
    """
    with respx.mock(assert_all_mocked=True, assert_all_called=False):
        yield
