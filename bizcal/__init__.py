__all__ = ['Day', 'BizDay', 'Calendar']

import datetime as pydt


class Day:
    def __init__(self, days=1):
        self.days = days

class BizDay:
    def __init__(self, days=1):
        self.days = days


class Date:
    def __init__(self, y, m, d, holiday=False):
        self.d = pydt.date(y, m, d)
        self.holiday = holiday

    @property
    def open(self):
        return self.d.weekday() < 5 and not self.holiday

    def __add__(self, days):
        d = self.d + pydt.timedelta(days)
        return Date(d.year, d.month, d.day)

    def __sub__(self, days):
        d = self.d + pydt.timedelta(-days)
        return Date(d.year, d.month, d.day)

    def __str__(self):
        tag = '*' if self.holiday else ''
        return self.d.strftime(f'%Y.%m.%d{tag}')
    __repr__ = __str__


class Calendar:
    def __init__(self, spec):
        if isinstance(spec, str):
            with open(spec) as f:
                spec = [s.strip() for s in f if s.strip()]
        cals = {}
        for line in spec:
            s = line.split(':')
            year = int(s[0])
            line = s[1]
            cals[year] = set(x for spec in line.split(',')
                             for x in parse_period(spec))
        if not cals:
            raise ValueError('invalid calendar spec')
        years = sorted(cals.keys())
        self.since = years[0]
        self.until = years[-1]
        if self.until - self.since + 1 < len(years):
            raise ValueError('incomplete calendar spec')
        self.table = [cals[y] for y in years]


def parse_period(spec):
    if '-' not in spec:
        yield int(spec)
        return
    s = spec.strip().split('-')
    if len(s) > 2:
        raise ValueError(f'invalid period spec {spec}')
    beg = int(s[0])
    end = int(s[0][:-len(s[1])] + s[1])
    day = pydt.date(2024, beg // 100, beg % 100)
    end = pydt.date(2024, end // 100, end % 100)
    oneday = pydt.timedelta(1)
    while day <= end:
        yield day.month * 100 + day.day
        day = day + oneday


### bizcal/__init__.py ends here
