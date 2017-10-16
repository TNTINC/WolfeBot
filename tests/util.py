import unittest.mock as mock
import asyncio

def _run(coro):
    """Helper to run async functions"""
    return asyncio.get_event_loop().run_until_complete(coro)

def AsyncMock(*args, **kwargs):
    """Helper to mock async functions"""
    m = mock.MagicMock(*args, **kwargs)

    async def mock_coro(*args, **kwargs):
        return m(*args, **kwargs)

    mock_coro.mock = m
    return mock_coro