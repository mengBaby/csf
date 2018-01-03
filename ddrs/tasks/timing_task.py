import sys
import os
import datetime
import json
import logging
import pandas
from uvtor.conf import settings
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from tasks.tasks import gen_everyday_summary, \
    gen_dynamodb_day_data, gen_everyday_item_summary, \
    gen_dynamodb_week_data, gen_dynamodb_month_data
from models.model import Store
from utils.engine_config import RS_ENGINE
from utils.time_utils import get_today_str, get_need_week, get_month_day

STORE_LIST = [
    (1000, '001'),
    (1001, '001'),
    (1002, '01'),
    (1003, '00'),
    (1006, '001'),
    (1010, '00'),
    (1013, '01'),
    (1012, '00'),
    (1009, '305'),
    (1007, '001'),
    (1011, '0001'),
    (1014, '00'),
    (1004, '0001'),
    (20000014, '03'),
    (20000013, '02'),
    (20000012, '06'),
]

WEEK_LIST = []


def get_week(monday):
    today = datetime.datetime.strptime(monday, '%Y-%m-%d')
    monday = today - datetime.timedelta(today.weekday())
    sunday = monday + datetime.timedelta(days=6)
    str_monday = monday.strftime('%Y-%m-%d')
    str_sunday = sunday.strftime('%Y-%m-%d')
    return str_monday, str_sunday


def date_compare(cm_id, foreign_store_id):
    select_query = """
        SELECT
            to_char(recorddate, 'YYYY-MM-DD') AS recorddate
        FROM
            goodsflow
        WHERE
            cmid = {}
        AND
            foreign_store_id = '{}'
        GROUP BY
            recorddate
    """.format(cm_id, foreign_store_id)
    gf_df = pandas.read_sql(select_query, RS_ENGINE)
    record_date = set(gf_df['recorddate'].values.tolist())
    query = """
        SELECT
            to_char(date, 'YYYY-MM-DD') AS date
        FROM
            ddrs_store_summary
        WHERE
            cmid = {}
        AND
            foreign_store_id = '{}'
        GROUP BY
            date;
    """.format(cm_id, foreign_store_id)
    store_df = pandas.read_sql(query, RS_ENGINE)
    store_date = set(store_df['date'].values.tolist())
    poor_set = record_date ^ store_date
    return poor_set


def start():
    print('执行 day task')
    last_day = get_today_str(days=-1)
    init_day = datetime.datetime.strptime('2016-01-01', '%Y-%m-%d')
    for store in Store.select():
        for day in date_compare(store.cm_id, store.foreign_store_id):
            d_day = datetime.datetime.strptime(day, '%Y-%m-%d')
            if d_day >= init_day:
                gen_everyday_summary.apply_async(
                    (store.cm_id, store.foreign_store_id, day),
                    link=gen_dynamodb_day_data.s(
                        store.cm_id, store.foreign_store_id, day, day))
                WEEK_LIST.append(day)
    return True


def week_start():
    last_monday, last_sunday = get_need_week()
    today = datetime.datetime.today()
    print('执行week task')
    for store in Store.select():
        gen_dynamodb_week_data.delay(True, store.cm_id, store.foreign_store_id,
                                     last_monday, last_sunday)
        for day in WEEK_LIST:
            if today.weekday() is 0:
                monday, sunday = get_week(day)
                gen_dynamodb_week_data.delay(
                    True, store.cm_id, store.foreign_store_id, monday, sunday)
    del WEEK_LIST[:]
    return True


def month_start():
    today = datetime.datetime.today()
    start_day, end_day = get_month_day(today.year, today.month - 1)
    start_day = start_day.strftime('%Y-%m-%d')
    end_day = end_day.strftime('%Y-%m-%d')
    for store in Store.select():
        gen_dynamodb_month_data.delay(
            True, store.cm_id, store.foreign_store_id, start_day, end_day)
    return True


def scheduler_listener(event):
    today = datetime.datetime.today()
    today = today.strftime('%Y-%m-%d')
    if event.exception:
        print('{} ---- timing_task任务监听结束状态...'.format(today))
    else:
        print('{}------timing_task任务照常运行...'.format(today))


def test():
    print('test')


def main():

    scheduler = BlockingScheduler(max_instances=1)
    scheduler.add_job(
        start,
        'cron',
        year='*',
        month='*',
        day='*',
        day_of_week='*',
        hour='*',
        minute='*/30',
        second=0)
    scheduler.add_job(
        week_start,
        'cron',
        year='*',
        month='*',
        day='*',
        day_of_week=0,
        hour=13,
        minute=30,
        second=0)
    scheduler.add_job(
        month_start,
        'cron',
        year='*',
        month='*',
        day=1,
        week='*',
        day_of_week='*',
        hour=14,
        minute=30,
        second=0)

    scheduler.add_job(
        week_start,
        'cron',
        year='*',
        month='*',
        day='*',
        day_of_week=0,
        hour=16,
        minute=30,
        second=0)
    scheduler.add_job(
        month_start,
        'cron',
        year='*',
        month='*',
        day=1,
        week='*',
        day_of_week='*',
        hour=17,
        minute=30,
        second=0)

    scheduler.add_listener(scheduler_listener,
                           EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == '__main__':
    main()
    # start()
    # for store in Store.select():
    #     print(store.cm_id, store.foreign_store_id)
    # res = date_compare(1000, '001')
    # for i in res:
    #     print(i)
    #     print(type(i))
