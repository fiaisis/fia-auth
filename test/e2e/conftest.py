"""
e2e session scoped fixtures
"""

import pytest
from src.db import ENGINE, Base


@pytest.fixture(scope="session", autouse=True)
def _setup():
    """
    Setup database pre-testing
    :return:
    """
    Base.metadata.drop_all(ENGINE)
    Base.metadata.create_all(ENGINE)
