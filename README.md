# Bizcal – Pythonic Business (Trading) Calendar

**Bizcal** is a simple business calendar package with three unique features:

- Compatibility: drop-in replacement of `datetime.date`.
- Pythonic: intuitive syntax.
- Holiday-aware: not just *when* not trading, but also *why*.

Bizcal is [listed on PyPI](https://pypi.org/project/bizcal/).

## Compatibility

Bizcal abstracts dates with class `Date` , which is a direct sub-class of the standard `datetime.date`.   This feature makes possible bizcal a drop-in replacement of `datime.date` to your legacy code bases.

In addition, `Date` defines a few handy methods and properties to help simplify your code.

## Pythonic

Code snippets speak for themselves.  Check more in [unit tests](./test/basic.py).

```python
from bizcal import Calendar

cne = Calendar([
    '2023: 0101-2, 0121-29, 0405, 0429-0503, 0622-25, 0929-1008',
    '2024: 0101, 0209-18, 0404-7, 0501-5, 0610, 0915-7, 1001-7',
])

day = cne('20240210')

# shift trading day with >> and <<
while not day:
    day = day >> 1

# shift calendar day with + and -
prev = day - 1
first_day_after_holiday = day and prev.holiday

# period abstraction
period = cne[20240101, 20240131]
print(len(period), 'trading days')

# iterate trading days
for day in period:
    print(f'{day} is a trading day')

# iterate calendar days
for day in period.days:
    flag = day and 'trading' or (day.holiday and 'holiday' or 'weekend')
    print(f'{day} is {flag}')
```

## Holiday-aware

Some exchanges (such as [SHFE](https://tsite.shfe.com.cn/eng/), [DCE](http://www.dce.com.cn/DCE/)) arrange trading hours according to holiday schedules.  Bizcal handles not only business (opening) and non-business (closing) days, but also tells if a non-business day is a holiday.

## API Reference

### Calendar definition

```python
from bizcal import Calendar
cal = Calendar('/path/to/calendar.file')
cal = Calendar([
    '2023: 0101-2, 0121-29, 0405, 0429-0503, 0622-25, 0929-1008',
    '2024: 0101, 0209-18, 0404-7, 0501-5, 0610, 0915-7, 1001-7',
])
```

Constructor `Calendar(spec)` accepts `spec` as a string or a list of strings.

- If `spec` is a string, it is accepted as a path to calendar definition file.  Each line defines calendar for one year by providing all holidays (may include weekends) of that year.
- If `spec` is a list of string, each string should be a line of calendar definition for one year.
- Year line format: `YYYY: holidays, holidays, ...`, where `holidays` should be a date range with format `MMDD`, `MMDD-DD` or `MMDD-MMDD`。

### Date creation

`Date` objects can only be created from a `Calendar` object with call syntax.  Multiple input formats are supported.

```python
cal = Calendar([...])
day = cal(20240501)     # integer
day = cal('20240501')   # YYYYMMDD (string)
day = cal('2024-05-01') # YYYY-MM-DD
day = cal('2024.05.01') # YYYY.MM.DD
day = cal(2024, 5, 1)   # year, month, day
day = cal((2024, 5, 1)) # tuple
day = cal([2024, 5, 1]) # list
day = cal([2025, 1, 1]) # error, as date is out of calendar scope
```

### Date manipulation

A `Date` object can be shifted back and forth as calendar or business day.  Operator `+` and `-` shifts as calendar day;  Operator `>>` and `<<` shifts as business day.

```python
cal = Calendar([...])
day = cal(20240501)

day + 10   # 2024-05-11
day - 1    # 2024-04-30

day >> 10  # 2024-05-17
day << 10  # 2024-04-17
```

### Date methods and properties

`Date` is sub-class of `datetime.date`, so apparently all `date` methods are supported.

- Extra properties
  - `Date.open`: is business day, boolean.
    - `Date.__bool__()`: bool operator, business day or not.
  - `Date.holiday`: is holiday, boolean.
  - `Date.num`: `YYYYMMDD` integer.
  - `Date.str`: `"YYYYMMDD"` string.
  - `Date.eom`: end-of-month boolean.
- Extra methods:
  - `Date.spec(sep='')`: `YYYY{sep}MM{sep}DD` string.
  - `Date.shift(days)`: explicit business day shift.


### Period definition

A period of dates can be defined with indexing (brackets) syntax.

```python
cal = Calendar([...])
period = cal[20240101, 20240131]
jan = cal['20240101-31']
q1 = cal['202401-3']
h1 = cal['202401-06']
years = cal['2023-4']

print(len(jan))  # count trading days
print(jan.spec)  # period spec string
```

The length of a period (`len(period)`) is the number of business days in that period.

### Period iteration

The primary use case of a period is date iteration.  Two generator properties `bizdays` and `days` are implemented for business day and calendar day iteration, respectively.  The default iteration method (`__iter__`) is business day.

```python
# iterate trading days
for day in cal['202401']:
    print(f'{day} is a trading day')

# iterate calendar days
for day in cal['20240215-20'].days:
    flag = day and 'trading' or (day.holiday and 'holiday' or 'weekend')
    print(f'{day} is {flag}')
```
