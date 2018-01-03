import sys
import timeit
import logging
import pandas
import datetime
import argparse
import peewee
from celery import group
from uvtor.conf import settings
from uvtor.db import models

from utils.time_utils import get_today_str
from tasks.tasks import gen_everyday_summary, \
    gen_everyday_item_summary, gen_dynamodb_day_data, \
    gen_dynamodb_week_data, gen_dynamodb_month_data
from models.model import StoreType, Store, ChainStore, Category
from tasks.tasks import gen_dynamodb_data, gen_test
from utils.engine_config import CHAIN_STORE_ENGINE
from tasks.sql_operation.dynamodb import save_day_data, create_table, \
    save_month_data, save_year_data, save_week_data, transform_cat_price_band
from tasks.sql_operation.select import Select


def gen_need_data():
    """
    生成summary 数据和
    :return:
    """
    parser = argparse.ArgumentParser(
        description='generate need data for store')
    parser.add_argument('--cm_id', type=int, help='cm id')
    parser.add_argument('--store_id', type=str, help='external store id')
    parser.add_argument('--task', type=str, help='external store id')
    parser.add_argument('--start', help='start date')
    parser.add_argument(
        '--end',
        help='end date for sale stats,\
                                           build date for loss stats')
    args = parser.parse_args()
    end = args.end
    start = args.start

    if args.cm_id and args.store_id:
        start_time = timeit.default_timer()
        print('{} -- {}'.format(start, end))
        if args.task == 'all':
            gen_everyday_summary.apply_async(
                (args.cm_id, args.store_id, start, end),
                link=gen_dynamodb_data.s(args.cm_id, args.store_id, start,
                                         end))
        if args.task == 'dashboard':
            print('task dashboard')
            gen_dynamodb_data.delay(True, args.cm_id, args.store_id, start,
                                    end)
        if args.task == 'price_band':
            print('task price band')
            gen_everyday_item_summary.apply_async(
                (args.cm_id, args.store_id, start, end),
                link=gen_dynamodb_week_data.s(args.cm_id, args.store_id, start,
                                              end))
        if args.task == 'month':
            gen_dynamodb_month_data.delay(True, args.cm_id, args.store_id,
                                          start, end)

        lapsed = timeit.default_timer() - start_time
        print('done! time: {}s'.format(lapsed))
    return True


def test(cmid):
    query = """
        SELECT
            "level",
            foreign_category_lv1 AS cat_lv1,
            foreign_category_lv1_name AS cat_lv1_name,
            foreign_category_lv2 AS cat_lv2,
            foreign_category_lv2_name AS cat_lv2_name,
            foreign_category_lv3 AS cat_lv3,
            foreign_category_lv3_name AS cat_lv3_name,
            foreign_category_lv4 AS cat_lv4,
            foreign_category_lv4_name AS cat_lv4_name
        FROM
            chain_category
        WHERE
            cmid = {}
    """.format(cmid)
    df = pandas.read_sql(query, CHAIN_STORE_ENGINE)
    data = df.to_dict('records')
    for i in data:
        cat = Category(
            cm_id=cmid,
            level=i['level'],
            foreign_category_lv1=i['cat_lv1'].strip()
            if i['cat_lv1'] else None,
            foreign_category_lv1_name=i['cat_lv1_name'].strip()
            if i['cat_lv1_name'] else None,
            foreign_category_lv2=i['cat_lv2'].strip()
            if i['cat_lv2'] else None,
            foreign_category_lv2_name=i['cat_lv2_name'].strip()
            if i['cat_lv2_name'] else None,
            foreign_category_lv3=i['cat_lv3'].strip()
            if i['cat_lv3'] else None,
            foreign_category_lv3_name=i['cat_lv3_name'].strip()
            if i['cat_lv3_name'] else None,
            foreign_category_lv4=i['cat_lv4'].strip()
            if i['cat_lv4'] else None,
            foreign_category_lv4_name=i['cat_lv4_name'].strip()
            if i['cat_lv4_name'] else None,
            last_update=datetime.datetime.now())
        cat.save()


if __name__ == "__main__":
    gen_need_data()

    # for data in data_dict:
    #     print(data['id'].replace(' ', '') + 'test')
    #     print(type(data['id']))
    # STORE_LIST = [
    #     1000,
    #     1001, 1002, 1003, 1006,
    #     1010, 1013, 1012, 1009, 1007, 1011, 1014,
    #     1004
    # ]
    # for i in STORE_LIST:
    #     test(i)
    # test(1006)
    # print('done!')
    # save_week_data(1000, '001')
    # create_table()
    # save_day_data(1000,
    #               '001',
    #               '2017-10-10',
    #               '2017-10-11')
    # save_week_data(1000,
    #                '001',
    #                '2016-10-10',
    #                '2017-10-11')

    # categories = Category.select(Category.level).where(
    #     Category.cm_id == 1000).order_by(
    #     Category.level.desc()).first()
    # print(categories.level)
