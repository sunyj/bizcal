# Bizcal – Pythonic Business (Trading) Calendar

**Bizcal** is a simple business calendar package with three unique features:

- Compatibility: `bizcal.Date` is a drop-in replacement for `datetime.date`.
- Pythonic: intuitive syntax.
- Holiday-aware: not just *when* not trading, but also *why*.

Bizcal is [listed on PyPI](https://pypi.org/project/bizcal/).

## Compatibility

Bizcal abstracts dates with `Date` class, a direct subclass of the standard
`datetime.date`, allowing it to seamlessly integrate into legacy codebases as
a drop-in replacement for `datetime.date`.

Additionally, `Date` includes several convenient methods and properties designed to simplify your code.

## Pythonic

Code snippets speak for themselves.  Check more in [unit tests](./test/basic.py).

```python
from bizcal import Calendar

cne = Calendar([
    '2023: 0101-2, 0121-29, 0405, 0429-0503, 0622-25, 0929-1008',
    '2024: 0101, 0209-18, 0404-7, 0501-5, 0608-10, 0914-17, 1001-7',
])

day = cne('20240210')

# shift trading day with >> and <<
while not day:
    day = day >> 1
prev_trading_day = day << 1
next_trading_day = day >> 1

# shift calendar day with + and -
yesterday = day - 1
tomorrow = day + 1

# period abstraction
period = cne[20240101, 20240131]
print(len(period), 'trading days')

# whole period
print(sum(1 for d in cne['*'].days if d.open), 'trading days')

# iterate trading days
for day in period:
    print(f'{day} is a trading day')

# iterate calendar days
for day in period.days:
    flag = day and 'trading' or (day.holiday and 'holiday' or 'weekend')
    print(f'{day} is {flag}')
```

## Holiday-aware

Certain exchanges, like [SHFE](https://tsite.shfe.com.cn/eng/) and [DCE](http://www.dce.com.cn/DCE/), adjust their trading hours based on holiday
schedules. Bizcal not only identifies business (open) and non-business
(closed) days but also specifies if a non-business day is a holiday.

## API Reference

### Calendar definition

```python
from bizcal import Calendar
cal = Calendar('/path/to/calendar.file')
cal = Calendar([
    '2023: 0101-2, 0121-29, 0405, 0429-0503, 0622-25, 0929-1008',
    '2024: 0101, 0209-18, 0404-7, 0501-5, 0608-10, 0914-17, 1001-7',
])
```

The `Calendar(spec)` constructor accepts `spec` as either a string or a list
of strings.

- If `spec` is a string, it is treated as a path to a calendar definition
  file. Each line in the file defines the holidays (and potentially weekends)
  for a specific year.
- If `spec` is a list of strings, each string represents a line of calendar
  definitions for one year.
- The year line format is `YYYY: holidays, holidays, ...`, where `holidays`
  are specified as date ranges in the format `MMDD`, `MMDD-DD`, or
  `MMDD-MMDD`.

### Date creation

`Date` objects can only be created from a `Calendar` object using call
syntax. Multiple input formats are supported.

```python
cal = Calendar([...])
day = cal(20240501)     # integer
day = cal('20240501')   # YYYYMMDD (string)
day = cal('2024-05-01') # YYYY-MM-DD
day = cal('2024.05.01') # YYYY.MM.DD
day = cal(2024, 5, 1)   # year, month, day
day = cal((2024, 5, 1)) # tuple
day = cal([2024, 5, 1]) # list
day = cal(date)         # date or even Date object
day = cal([2025, 1, 1]) # error, as date is out of calendar scope
```

### Date manipulation

A `Date` object can be shifted both as calendar days and business days. The
`+` and `-` operators shift the date as calendar days, while the `>>` and `<<`
operators shift the date as business days.

```python
cal = Calendar([...])
day = cal(20240501)

day + 10   # 2024-05-11
day - 1    # 2024-04-30

day >> 10  # 2024-05-17
day << 10  # 2024-04-17
```

### Date methods and properties

`Date` is a subclass of `datetime.date`, so all `date` methods are supported.

#### Extra Properties

- `Date.open`: Indicates if it is a business day (boolean).
  - `Date.__bool__()`: Boolean operator, returns if it is a business day.
- `Date.holiday`: Indicates if it is a holiday (boolean).
- `Date.num`: Returns the date as an `YYYYMMDD` integer.
- `Date.str`: Returns the date as a `"YYYYMMDD"` string.
- `Date.eom`: Indicates if it is the end of the month (boolean).

#### Extra Methods

- `Date.spec(sep='')`: Returns the date as a `YYYY{sep}MM{sep}DD` string.
- `Date.shift(days)`: Performs an explicit business day shift.

### Period definition

A period of dates can be defined using the indexing (brackets) syntax.

```python
cal = Calendar([...])
period = cal[20240101, 20240131]
jan = cal['20240101-31']
q1 = cal['202401-3']
h1 = cal['202401-06']
years = cal['2023-4']

period = cal[cal('20240101'), cal(2024, 1, 1) + 30]

print(len(jan))  # count trading days
print(jan.spec)  # period spec string
```

The length of a period (`len(period)`) is the number of business days in that
period.

### Period iteration

The primary use case of a period is date iteration. Two generator properties,
`bizdays` and `days`, are implemented for business day and calendar day
iteration, respectively. The default iteration method (`__iter__`) is for
business days.

```python
# iterate business days
for day in cal['202401']:
    print(f'{day} is a trading day')

# iterate calendar days
for day in cal['20240215-20'].days:
    flag = day and 'trading' or (day.holiday and 'holiday' or 'weekend')
    print(f'{day} is {flag}')
```
### Date span parsing

Static method `Calendar.span(spec: str)` parses a string spec into
`(beg, end)` tuple of dates.  `datetime.date` objects are returned.

```python
from bizcal import Calendar

beg, end = Calendar.span('202402')
```
