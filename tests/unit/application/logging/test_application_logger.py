import logging
from uuid import uuid4

import pytest

from earth_twin_engine.application.logging import (
    ApplicationLogger,
)


@pytest.fixture
def application_logger() -> ApplicationLogger:
    logger = logging.getLogger(f"test.application.logger.{uuid4().hex}")
    logger.setLevel(logging.DEBUG)
    logger.propagate = True

    return ApplicationLogger(logger)
