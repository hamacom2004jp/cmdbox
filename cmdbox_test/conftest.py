"""
Pytest configuration and fixtures for cmdbox testing
"""
import pytest
import logging
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock


@pytest.fixture
def temp_data_dir():
    """Create a temporary data directory for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_logger():
    """Create a mock logger for testing"""
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)
    return logger


@pytest.fixture
def mock_args():
    """Create a mock argparse.Namespace for testing"""
    args = Mock()
    args.host = "localhost"
    args.port = 6379
    args.password = "password"
    args.svname = "test_server"
    args.data = None
    args.format = "json"
    args.output_json = None
    args.output_json_append = False
    args.stdout_log = True
    args.capture_stdout = True
    args.capture_maxsize = 1024 * 1024 * 10
    return args


@pytest.fixture
def mock_redis_client():
    """Create a mock Redis client for testing"""
    client = MagicMock()
    client.check_server = MagicMock(return_value=True)
    client.list_server = MagicMock(return_value=[
        {
            "svname": "test_server",
            "pid": 12345,
            "model": "test_model"
        }
    ])
    return client


@pytest.fixture
def version_mock():
    """Create a mock version object"""
    ver = Mock()
    ver.__appid__ = "cmdbox"
    ver.__version__ = "0.2.0"
    return ver
