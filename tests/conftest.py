import os
import tempfile

import pytest
from main import __call__

@pytest.fixture(scope='module')
def test_client():
    app = __call__('Testing')

    testing_client = app.test_client()

    ctx = app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()
