from dateutil import parser, tz
import datetime
import pandas
import calendar


def get_last_year_date(days=365):
    """
    获取一年前的今天
    :param days:
    :return:
    """
    today = datetime.datetime.today()
    monday = today - datetime.timedelta(today.weekday())
    last_day = monday - datetime.timedelta(days=days)
    return last_day


def get_need_week(weeks=1, days=1):
    today = datetime.datetime.today()
    monday = today - datetime.timedelta(today.weekday())
    last_monday = monday - datetime.timedelta(weeks=weeks)
    last_sunday = monday - datetime.timedelta(days=days)
    str_last_monday = last_monday.strftime('%Y-%m-%d')
    str_last_sunday = last_sunday.strftime('%Y-%m-%d')
    return str_last_monday, str_last_sunday


def get_today_str(days=None, weeks=None):
    today = datetime.datetime.today()
    if days:
        last_day = today + datetime.timedelta(days=days)
        return last_day.strftime('%Y-%m-%d')
    if weeks:
        last_day = today + datetime.timedelta(weeks=weeks)
        return last_day.strftime('%Y-%m-%d')

    return today.strftime('%Y-%m-%d')


def get_month_last(date):
    if isinstance(date, pandas.Timestamp):
        date = date.to_datetime()
    first_day, last_day = get_month_day(date.year, date.month)
    return last_day


def is_year(year):
    if year % 400 == 0:
        return True
    elif (year % 100) != 0 and (year % 4 == 0):
        return True
    else:
        return False


def get_last_week(monday):
    monday_date = datetime.datetime.strptime(monday, '%Y-%m-%d')
    last_monday = monday_date - datetime.timedelta(days=7)
    last_sunday = monday_date - datetime.timedelta(days=1)
    return last_monday, last_sunday


def get_month_day(year, month):
    firstDayWeekDay, monthRange = calendar.monthrange(year, month)
    first_day = datetime.date(year=year, month=month, day=1)
    last_day = datetime.date(year=year, month=month, day=monthRange)
    return first_day, last_day


def get_thirteen_week_day(year_start):
    now = datetime.datetime.now()
    week = now.isocalendar()[1]
    if week >= 13:
        start_week = week - 13
    else:
        start_week = 1
    start_days = datetime.timedelta(weeks=start_week - 1)
    end_days = datetime.timedelta(weeks=week - 1) - datetime.timedelta(1)
    start_monday = year_start + start_days
    last_sunday = year_start + end_days
    last_monday = last_sunday - datetime.timedelta(6)
    return start_monday, last_sunday, last_monday


def dateline(start, end):
    if not isinstance(start, datetime.datetime):
        start = parser.parse(start).astimezone(tz.gettz('Asia/Shanghai'))
    if not isinstance(end, datetime.datetime):
        end = parser.parse(end).astimezone(tz.gettz('Asia/Shanghai'))
    start = datetime.datetime(
        start.year, start.month,
        start.day, tzinfo=tz.gettz('Asia/Shanghai'))
    end = datetime.datetime(
        end.year, end.month,
        end.day,
        tzinfo=tz.gettz('Asia/Shanghai')) + datetime.timedelta(days=1)
    return [start + datetime.timedelta(days=_i) for _i in range(
        int((end - start).total_seconds() / (3600 * 24)))]
