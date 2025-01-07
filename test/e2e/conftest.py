"""e2e session scoped fixtures"""

import pytest

from fia_auth.db import ENGINE, Base


@pytest.fixture(scope="session", autouse=True)
def _setup():
    """Set up database pre-testing"""
    Base.metadata.drop_all(ENGINE)
    Base.metadata.create_all(ENGINE)
