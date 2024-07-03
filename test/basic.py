import unittest, json
from bizcal import *
from bizcal import parse_range
import datetime as pydt


class TestBasic(unittest.TestCase):

    def test_parse_range(self):
        with self.assertRaises(ValueError):
            parse_range('1-2-3')
        self.assertEqual(parse_range('abc'), ('abc', 'abc'))
        self.assertEqual(parse_range('abc-1234'), ('abc', '1234'))
        self.assertEqual(parse_range('1234-56'), ('1234', '1256'))
        self.assertEqual(parse_range('1234-4567'), ('1234', '4567'))
        self.assertEqual(parse_range('1234-12345'), ('1234', '12345'))
        self.assertEqual(parse_range('1234-5'), ('1234', '1235'))
        self.assertEqual(parse_range(''), ('', ''))


    def test_spec(self):
        spec = ['2023: 0101-2,0121-27,0405,0429-0503,0622-24,0929-1006',
                '2024: 0101,0210-7,0404-6,0501-5,0610,0915-7,1001-7']
        s = Calendar(spec)
        self.assertEqual(len(s.table), 2)
        self.assertEqual(len(s.table[0]), 26)
        self.assertEqual(len(s.table[1]), 28)

        s = Calendar(['2023: 0228-0301', '2024: 0228-0301'])
        self.assertEqual(len(s.table), 2)
        self.assertEqual(len(s.table[0]), 2)
        self.assertEqual(len(s.table[1]), 3)


    def test_holiday(self):
        cal = Calendar(['2024: 0101,0210-7,0404-6,0501-5,0610,0915-7,1001-7'])
        self.assertTrue(20240701 in cal)
        self.assertFalse(cal(20240501).open)
        with self.assertRaises(ValueError):
            cal(20230501).biz
        with self.assertRaises(ValueError):
            cal(20990501).biz
        self.assertTrue(cal(20240501).holiday)
        self.assertTrue(cal(20240101).holiday)
        self.assertFalse(cal(20241231).holiday)
        self.assertTrue(cal([2024, 5, 1]).holiday)
        self.assertTrue(cal((2024, 1, 1)).holiday)
        self.assertTrue(cal(2024, 1, 1).holiday)


    def test_bizdays(self):
        cal = Calendar(['2024: 0101,0210-7,0404-6,0501-5,0610,0915-7,1001-7'])
        days = list(cal[20240101, '2024-01.05'].bizdays)
        self.assertEqual(len(days), 4)
        self.assertEqual(days[-1].strftime('%Y%m%d'), '20240105')
        span = cal[20240210, 20240215]
        self.assertEqual(list(span), [])
        self.assertEqual(len(list(span.days)), 6)
        self.assertEqual(len(list(cal['20240101-5'])), 4)
        self.assertEqual(len(list(cal['20240901-30'])), 19)
        self.assertEqual(list(cal['20240101']), [])


    def test_date(self):
        cal = Calendar(['2024: 0101,0210-7,0404-6,0501-5,0610,0915-7,1001-7'])
        day = cal(20240101)
        self.assertEqual(day.idx, 0)
        self.assertFalse(day.open)
        self.assertFalse(day)
        self.assertFalse(cal(2024, 5, 1).open)
        self.assertTrue(cal(20240501).holiday)
        self.assertTrue(cal('20240501').holiday)
        self.assertTrue(cal(2024, 5, 1).holiday)
        self.assertTrue(cal([2024, 5, 1]).holiday)
        self.assertTrue(cal((2024, 5, 1)).holiday)


    def test_cal_shift(self):
        cal = Calendar(['2024: 0101,0210-7,0404-6,0501-5,0610,0915-7,1001-7'])
        day = cal(20240101) + 1
        self.assertTrue(day.open)
        self.assertEqual(day.strftime('%Y%m%d'), '20240102')

        day = cal(20240228) + 1
        self.assertTrue(day.open)
        self.assertEqual(day.strftime('%Y%m%d'), '20240229')
        day = day - 1
        self.assertEqual(day.strftime('%Y%m%d'), '20240228')


    def test_biz_shift(self):
        cal = Calendar(['2024: 0101,0210-7,0404-6,0501-5,0610,0915-7,1001-7'])
        d = cal(20240101) >> 10
        self.assertEqual(d.strftime('%Y%m%d'), '20240115')
        d = d << 9
        self.assertEqual(d.strftime('%Y%m%d'), '20240102')
        with self.assertRaises(ValueError):
            d << 10


### test/basic.py ends here
