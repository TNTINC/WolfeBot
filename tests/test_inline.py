import unittest
import unittest.mock as mock

import bot as wolfe

class test_inline(unittest.TestCase):
    @mock.patch("bot.con")
    def test_inline_calls_con(self, mock_con):
        mock_fetchall = mock.MagicMock()
        mock_fetchall.fetchall.return_value = [
            ("", "")
        ]
        mock_con.execute.return_value = mock_fetchall

        wolfe.inline(mock.MagicMock())

        mock_con.execute.assert_called_once()
        mock_fetchall.fetchall.assert_called_once()