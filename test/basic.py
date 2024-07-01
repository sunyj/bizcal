import unittest, json
from bizcal import *

class TestBasic(unittest.TestCase):

    def test_spec_read(self):
        spec = ['2023: 0101-2, 0121-27, 0405, 0429-0503, 0622-24, 0929-1006',
                '2024: 0101, 0210-7, 0404-6, 0501-5, 0610, 0915-7, 1001-7']
        s = Calendar(spec)
        self.assertEqual(len(s.table), 2)
        self.assertEqual(len(s.table[0]), 26)
        self.assertEqual(len(s.table[1]), 28)

        s = Calendar(['2023: 0228-0301', '2024: 0228-0301'])
        self.assertEqual(len(s.table), 2)
        self.assertEqual(len(s.table[0]), 2)
        self.assertEqual(len(s.table[1]), 3)

### test/basic.py ends here
