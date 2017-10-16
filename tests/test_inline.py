import unittest
import unittest.mock as mock

import bot as wolfe

def get_mock_fetchall(mock_con, return_value=[("","")]):
    mock_fetchall = mock.MagicMock()
    mock_fetchall.fetchall.return_value = return_value
    mock_con.execute.return_value = mock_fetchall
    return mock_fetchall

class test_inline(unittest.TestCase):
    
    @mock.patch("bot.con")
    def test_inline_calls_con(self, mock_con):
        mock_fetchall = get_mock_fetchall(mock_con)
        
        wolfe.inline(mock.MagicMock())

        mock_con.execute.assert_called_once()
        mock_fetchall.fetchall.assert_called_once()
    
    @mock.patch("bot.con")
    def test_inline_answers_request(self, mock_con):
        mock_req = mock.MagicMock()
        mock_fetchall = get_mock_fetchall(mock_con)

        wolfe.inline(mock_req)

        mock_req.answer.assert_called_once()
