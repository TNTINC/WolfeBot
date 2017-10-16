import unittest
import unittest.mock as mock
import aiotg
import asyncio
import re

import bot as wolfe

from tests.util import _run, AsyncMock

class test_misc(unittest.TestCase):
    # Just make sure there send something.
    def test_keo(self):
        m = mock.create_autospec(aiotg.Chat)
        wolfe.keo(m, None)
        m.send_text.assert_called_once()

    def test_owo(self):
        m = mock.create_autospec(aiotg.Chat)
        wolfe.owo(m, None)
        m.send_text.assert_called_once()

    def test_fml(self):
        m = mock.create_autospec(aiotg.Chat)
        wolfe.weather(m, None)
        m.reply.assert_called_once()

    def test_yiffme(self):
        test_string = "verb"
        test_username = "keo"
        chat = mock.create_autospec(aiotg.Chat)
        chat.message = {"from":{}}
        chat.message["from"]["first_name"] = test_username
        mock_match = mock.create_autospec(re.match("",""))
        mock_match.group.return_value = test_string

        wolfe.yiffme(chat, mock_match)

        mock_match.group.assert_called_once_with(1)
        chat.send_text.assert_called_once_with('*verbs keo*')


    def test_welcome(self):
        m = mock.MagicMock()
        m.send_sticker = AsyncMock()
        m.send_text = AsyncMock()
        _run(wolfe.welcome(m, None))
        m.send_sticker.mock.assert_called_once()
        m.send_text.mock.assert_called_once()

