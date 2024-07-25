import unittest, json
from bizcal import *
from bizcal import parse_range
import datetime as pydt


class TestBasic(unittest.TestCase):

    def test_parse_range(self):
        with self.assertRaises(ValueError):
            parse_range('1-2-3')
        self.assertEqual(parse_range('abc'), ('abc', 'abc'))
        self.assertEqual(parse_range('000-1234'), ('000', '1234'))
        self.assertEqual(parse_range('1234-56'), ('1234', '1256'))
        self.assertEqual(parse_range('1234-4567'), ('1234', '4567'))
        self.assertEqual(parse_range('1234-12345'), ('1234', '12345'))
        self.assertEqual(parse_range('1234-5'), ('1234', '1235'))
        self.assertEqual(parse_range(''), ('', ''))


    def test_spec(self):
        spec = ['2023: 0101-2,0121-27,0405,0429-0503,0622-24,0929-1006',
                '2024: 0101,0210-7,0404-6,0501-5,0610,0915-7,1001-7']
        cal = Calendar(spec)
        self.assertEqual(len(cal.table), 2)
        self.assertEqual(len(cal.table[0]), 26)
        self.assertEqual(len(cal.table[1]), 28)

        cal = Calendar(['2023: 0228-0301', '2024: 0228-0301'])
        self.assertEqual(len(cal.table), 2)
        self.assertEqual(len(cal.table[0]), 2)
        self.assertEqual(len(cal.table[1]), 3)

        d1 = pydt.date(2023, 1, 1)
        d2 = pydt.date(2023, 1, 9)
        self.assertFalse(cal(d1).open)
        self.assertFalse(cal(cal(d1)).open)
        self.assertTrue(cal(d2).open)
        self.assertEqual(len(cal[d1, d2]), 6)


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


    def test_helpers(self):
        from bizcal import first_day, last_day, range_join
        self.assertEqual(first_day('20240101').strftime('%Y%m%d'), '20240101')
        self.assertEqual(first_day('202401').strftime('%Y%m%d'), '20240101')
        self.assertEqual(first_day('2020').strftime('%Y%m%d'), '20200101')
        self.assertEqual(last_day('20240101').strftime('%Y%m%d'), '20240101')
        self.assertEqual(last_day('202401').strftime('%Y%m%d'), '20240131')
        self.assertEqual(last_day('202402').strftime('%Y%m%d'), '20240229')
        self.assertEqual(last_day('202202').strftime('%Y%m%d'), '20220228')
        self.assertEqual(last_day('202002').strftime('%Y%m%d'), '20200229')
        self.assertEqual(last_day('2024').strftime('%Y%m%d'), '20241231')

        self.assertEqual(range_join('', ''), '')
        self.assertEqual(range_join('123', '4567'), '123-4567')
        self.assertEqual(range_join('abc100', 'abc101'), 'abc100-1')
        self.assertEqual(range_join('abc100', 'abc999'), 'abc100-999')
        self.assertEqual(range_join('abc100', 'abc100'), 'abc100')
        self.assertEqual(range_join('abc', '100'), 'abc-100')
        self.assertEqual(range_join('abc', ''), 'abc-')
        self.assertEqual(range_join('', 'abc'), '-abc')


    def test_range(self):
        cal = Calendar([
            '2023: 0101-2,0121-27,0405,0429-0503,0622-24,0929-1006',
            '2024: 0101,0210-7,0404-6,0501-5,0610,0915-7,1001-7'])

        self.assertEqual(len(cal['202401']), 22)
        self.assertEqual(len(cal['202401-2']), 38)

        days = list(cal[20240101, '2024-01.05'].bizdays)
        self.assertEqual(len(days), 4)
        self.assertEqual(days[-1].num, 20240105)
        span = cal[20240210, 20240215]
        self.assertEqual(list(span), [])
        self.assertEqual(len(list(span.days)), 6)
        self.assertEqual(len(list(cal['20240101-5'])), 4)
        self.assertEqual(len(list(cal['20240901-30'])), 19)
        self.assertEqual(list(cal['20240101']), [])
        self.assertEqual(len(cal['2024.0101-5']), 4)
        self.assertEqual(len(cal[20240210, 20240215]), 0)
        self.assertEqual(cal[20240201, 20240205].spec, '20240201-5')
        self.assertEqual(cal[20240201, 20240220].spec, '20240201-20')
        self.assertEqual(cal[20240201, 20241225].spec, '20240201-1225')
        self.assertEqual(cal[20240101, 20240229].spec, '202401-2')
        self.assertEqual(cal[20240101, 20241231].spec, '2024')
        self.assertEqual(cal[20230101, 20241231].spec, '2023-4')


    def test_date(self):
        cal = Calendar(['2024: 0101,0210-7,0404-6,0501-5,0610,0915-7,1001-7'])
        day = cal(20240101)
        self.assertEqual(day.num, 20240101)
        self.assertEqual(day.str, '20240101')
        self.assertEqual(day.spec('-'), '2024-01-01')
        self.assertEqual(day.idx, 0)
        self.assertFalse(day.open)
        self.assertFalse(day)
        self.assertFalse(cal(2024, 5, 1).open)

        self.assertTrue(cal(20240501).holiday)
        self.assertTrue(cal('20240501').holiday)
        self.assertTrue(cal(2024, 5, 1).holiday)
        self.assertTrue(cal([2024, 5, 1]).holiday)
        self.assertTrue(cal((2024, 5, 1)).holiday)
        self.assertTrue(cal(pydt.date(2024, 5, 1)).holiday)


    def test_cal_shift(self):
        cal = Calendar(['2024: 0101,0210-7,0404-6,0501-5,0610,0915-7,1001-7'])
        day = cal(20240101) + 1
        self.assertTrue(day.open)
        self.assertEqual(day.str, '20240102')

        day = cal(20240228) + 1
        self.assertTrue(day.open)
        self.assertEqual(day.num, 20240229)
        day = day - 1
        self.assertEqual(day.str, '20240228')


    def test_biz_shift(self):
        cal = Calendar(['2024: 0101,0210-7,0404-6,0501-5,0610,0915-7,1001-7'])
        d = cal(20240101) >> 10
        self.assertEqual(d.str, '20240115')
        d = d << 9
        self.assertEqual(d.str, '20240102')
        with self.assertRaises(ValueError):
            d << 10


    def test_span(self):
        self.assertEqual(Calendar.span('202402'),
                         (pydt.date(2024, 2, 1), pydt.date(2024, 2, 29)))
        self.assertEqual(Calendar.span('202401-3'),
                         (pydt.date(2024, 1, 1), pydt.date(2024, 3, 31)))
        self.assertEqual(Calendar.span('20240101'),
                         (pydt.date(2024, 1, 1), pydt.date(2024, 1, 1)))


### test/basic.py ends here
