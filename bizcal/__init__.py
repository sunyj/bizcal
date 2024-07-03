__all__ = ['Calendar']

import re
import datetime as pydt


class Date(pydt.date):
    def __new__(cls, y, m, d, cal, idx=None, holiday=None, biz=None,
                *, _internal=None):
        if not _internal:
            raise TypeError('Date is an internal type, do NOT use it!')
        day = pydt.date.__new__(cls, y, m, d)
        day.cal = cal
        day.idx = cal._idx(day) if idx is None else idx
        if holiday is None:
            day.holiday = day.month * 100 + day.day in cal.table[day.idx]
        else:
            day.holiday = holiday
        day.open = not day.holiday and day.weekday() < 5 if biz is None else biz
        return day


    def clone(self):
        return Date(self.year, self.month, self.day, self.cal,
                    self.idx, self.holiday, self.open, _internal=True)

    @property
    def num(self): return self.year * 10000 + self.month * 100 + self.day

    def __eq__(self, d):
        if isinstance(d, Date):
            return self.num == d.num
        return (self.year == d.year and self.month == d.month
                and self.day == d.day)


    def __add__(self, days):
        "Shift calendar days."
        if not days:
            return self.clone()
        d = pydt.date.fromordinal(self.toordinal() + days)
        return Date(d.year, d.month, d.day, self.cal,
                    self.idx if d.year == self.year else None, _internal=True)

    def __sub__(self, days):
        return self + (-days)


    def __rshift__(self, days):
        "Shift business days."
        return self.shift(days)

    def __lshift__(self, days):
        return self.shift(-days)

    def shift(self, days):
        if not days:
            return self.clone()
        delta = days > 0 and 1 or -1
        days = abs(days)
        day = self.clone()
        while days:
            day = day + delta
            days -= (day.open and 1 or 0)
        return day


class Calendar:
    def __init__(self, spec):
        if isinstance(spec, str):
            with open(spec) as f:
                spec = [s.strip() for s in f if s.strip()]
        cals = {}
        for line in spec:
            s = line.split(':')
            cals[int(s[0])] = set(x for spec in s[1].split(',')
                                  for x in parse_mmdd(int(s[0]), spec))
        if not cals:
            raise ValueError('invalid calendar spec')
        years = sorted(cals.keys())
        self.ymin = years[0]
        self.ymax = years[-1]
        if self.ymax - self.ymin + 1 < len(years):
            raise ValueError('incomplete calendar spec')
        self.table = [cals[y] for y in years]
        assert len(self.table) == self.ymax - self.ymin + 1

    def _parse_date(self, spec):
        if isinstance(spec, str):
            return self._parse_date(int(re.sub(r'\D', '', spec)))
        if isinstance(spec, (list, tuple)):
            return self._parse_date(pydt.date(*spec))
        if isinstance(spec, pydt.date):
            d = spec
        else:
            if spec < 19000000 or spec > 29999999:
                raise ValueError(f'invalid date number {spec}')
            year = spec // 10000
            mmdd = spec % 10000
            d = pydt.date(year, mmdd // 100, mmdd % 100)
        return (d, self._idx(d))

    def _idx(self, d):
        if d.year < self.ymin or d.year > self.ymax:
            raise ValueError(f'{d} outside [{self.ymin}, {self.ymax}]')
        return d.year - self.ymin

    def is_holiday(self, spec):
        d, idx = self._parse_date(spec)
        return d.month*100 + d.day in self.table[idx]


    def is_open(self, spec):
        d, idx = self._parse_date(spec)
        return d.weekday() < 5 and d.month * 100 + d.day not in self.table[idx]

    def __contains__(self, spec):
        return self.is_open(spec)


    def day(self, *args):
        if len(args) == 3:
            return Date(args[0], args[1], args[2], self, _internal=True)
        if len(args) == 1:
            d, idx = self._parse_date(args[0])
            return Date(d.year, d.month, d.day, self, idx, _internal=True)

    def __call__(self, *spec):
        return self.day(*spec)


    def bizdays(self, since, until=None):
        "Generate business days."

        if until is None:
            if not isinstance(since, str):
                raise TypeError('only string allowed in single-param bizdays')
            since, until = parse_range(since)
        d, _ = self._parse_date(since)
        end, _ = self._parse_date(until)
        one = pydt.timedelta(1)
        while d <= end:
            idx = self._idx(d)
            holiday = d.month * 100 + d.day in self.table[idx]
            if d.weekday() < 5 and not holiday:
                yield Date(d.year, d.month, d.day, self,
                           idx, holiday, True, _internal=True)
            d += one


def parse_mmdd(year, spec):
    if '-' not in spec:
        yield int(spec)
        return
    beg, end = parse_range(spec, numeric=True)
    day = pydt.date(year, beg // 100, beg % 100)
    end = pydt.date(year, end // 100, end % 100)
    oneday = pydt.timedelta(1)
    while day <= end:
        yield day.month * 100 + day.day
        day = day + oneday


def parse_range(spec, numeric=False):
    if numeric:
        s = parse_range(spec, False)
        return (int(s[0]), int(s[1]))
    s = spec.strip().split('-')
    if len(s) > 2:
        raise ValueError(f'invalid range spec {spec}')
    if len(s) < 2:
        return (spec, spec)
    if len(s[0]) < len(s[1]):
        return (s[0], s[1])
    return (s[0], s[0][:-len(s[1])] + s[1])


### bizcal/__init__.py ends here
