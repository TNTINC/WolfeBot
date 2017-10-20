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

    @mock.patch("bot.con")
    def test_inline_populates_answer_single(self, mock_con):
        mock_fetchall = get_mock_fetchall(
            mock_con,
            return_value=[
            ("MOCK_TG_ID", "MOCK_ID")
        ])
        mock_req = mock.MagicMock()

        wolfe.inline(mock_req)

        self.assertEqual(mock_req.answer.call_args, mock.call(
            results=[{
                'type':'photo',
                'id': "MOCK_ID",
                'photo_file_id': "MOCK_TG_ID"
            }],
            cache_time=0,
            is_personal=True,
            next_offset='Yolo'
        ))
    @mock.patch("bot.con")
    def test_inline_poplates_answer_multiple(self, mock_con):
        r = [(i, str(i)) for i in range(20)]
        mock_fetchall = get_mock_fetchall(mock_con,                
                return_value=r
            )
        mock_req = mock.MagicMock()

        wolfe.inline(mock_req)

        flag = False

        check = [{'type':'photo', 'id': t, 'photo_file_id': i} for i, t in r]

        for res in mock_req.answer.call_args[1]["results"]:
            if not res in check:
                print(res)
                print("---")
                print(check[0])
                flag = True
                break
        
        self.assertFalse(flag, msg="Returned result that was not passed in")


