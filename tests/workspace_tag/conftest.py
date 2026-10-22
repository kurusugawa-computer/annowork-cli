from unittest.mock import MagicMock

import pytest
from annoworkapi.resource import Resource


@pytest.fixture
def service():
    result = MagicMock(spec=Resource)
    result.api = MagicMock()
    result.wrapper = MagicMock()
    return result
