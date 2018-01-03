from uvtor.core.decorators.api import standard_api
from utilib.utils.timezone import to_str
from uvtor.core import settings
from apps.ring_analysis.handlers import BaseHandler
from uvtor.db.models import manager
from models.model import Category
from utils.auth import login_required
from utils import ddrs_utils as dus
from utils import time_utils as tus
import pandas
import numpy
import json

dynamoDB_app = settings.dynamoDB_app


def _calculate_profit_rote(sale, profit):
    if sale == 0 or numpy.isnan(sale):
        return 0
    else:
        return profit / sale * 100


async def get_cat_sales(cat_info, keys):
    sales_list = await dynamoDB_app.async_batch_get_item('sales', keys)
    if len(sales_list) == 0:
        return [], []
    cat_sales = pandas.read_json(json.dumps(sales_list))
    sales_data = pandas.merge(cat_info, cat_sales)
    sales_data = sales_data.drop_duplicates(['key'])
    cat_l2_sales_df = sales_data.groupby(['cat_l1_id',
                                          'cat_l1_name',
                                          'cat_l2_id',
                                          'cat_l2_name'],
                                         as_index=False). \
        agg({'value': numpy.sum})
    cat_l2_sales_df['cat_l1_sales'] = cat_l2_sales_df.groupby(
        ['cat_l1_id'])['value'].transform(sum)
    cat_l2_sales_df.sort_values(
        by=['cat_l1_sales', 'cat_l1_id', 'value', 'cat_l2_id'],
        ascending=[0, 1, 0, 1],
        inplace=True)
    cat_l2_sales_df['cat_l2_name'] = cat_l2_sales_df[
        'cat_l2_name'].apply(str.strip)
    cat_l1_sales_df = cat_l2_sales_df[[
        'cat_l1_id', 'cat_l1_name', 'cat_l1_sales'
    ]].drop_duplicates().sort_values(
        by=['cat_l1_sales', 'cat_l1_id'], ascending=[0, 1])
    cat_l1_sales_df['cat_l1_name'] = cat_l1_sales_df[
        'cat_l1_name'].apply(str.strip)
    cat_l1_sales = cat_l1_sales_df.to_dict('records')
    cat_l2_sales = cat_l2_sales_df[[
        'cat_l1_id', 'cat_l2_id', 'cat_l2_name', 'value'
    ]].to_dict('records')
    return cat_l1_sales, cat_l2_sales


async def get_cat_profit(cat_info, keys):
    profit_list = await dynamoDB_app.async_batch_get_item('profit', keys)
    if len(profit_list) == 0:
        return [], []
    cat_profit = pandas.read_json(json.dumps(profit_list))
    profit_data = pandas.merge(cat_info, cat_profit)
    profit_data = profit_data.drop_duplicates(['key'])
    cat_l2_profit_df = profit_data.groupby(['cat_l1_id',
                                            'cat_l1_name',
                                            'cat_l2_id',
                                            'cat_l2_name'],
                                           as_index=False). \
        agg({'value': numpy.sum})
    cat_l2_profit_df['cat_l1_profit'] = cat_l2_profit_df.groupby(
        ['cat_l1_id'])['value'].transform(sum)
    cat_l2_profit_df['value'][cat_l2_profit_df['value'] < 0] = 0
    cat_l2_profit_df.sort_values(
        by=['cat_l1_profit', 'cat_l1_id', 'value', 'cat_l2_id'],
        ascending=[0, 1, 0, 1],
        inplace=True)
    cat_l1_profit_df = cat_l2_profit_df[[
        'cat_l1_id', 'cat_l1_name', 'cat_l1_profit'
    ]].drop_duplicates().sort_values(
        by=['cat_l1_profit', 'cat_l1_id'], ascending=[0, 1])
    cat_l1_profit_df['cat_l1_profit'][cat_l1_profit_df['cat_l1_profit'] < 0] \
        = 0
    cat_l1_profit = cat_l1_profit_df.to_dict('records')
    cat_l2_profit = cat_l2_profit_df[[
        'cat_l1_id', 'cat_l2_id', 'cat_l2_name', 'value'
    ]].to_dict('records')
    return cat_l1_profit, cat_l2_profit


async def get_sales(cat_info):
    cat_info = pandas.read_json(
        json.dumps(cat_info)).drop_duplicates(
        ['key'])
    cat_keys = cat_info['key'].tolist()
    keys = []
    for k in cat_keys:
        key = {}
        key['key'] = k
        keys.append(key)
    sales_list = await dynamoDB_app.async_batch_get_item('sales', keys)
    if len(sales_list) == 0:
        return []
    cat_sales = pandas.read_json(json.dumps(sales_list))
    sales_data = pandas.merge(cat_info, cat_sales)
    sales_data = sales_data.drop_duplicates(['key'])
    cat_sales_df = sales_data.groupby(['cat_id',
                                       'cat_name'],
                                      as_index=False). \
        agg({'value': numpy.sum})

    cat_sales_df.sort_values(
        by=['value', 'cat_id'],
        ascending=[0, 1],
        inplace=True)
    return cat_sales_df


async def get_profit(cat_info):
    cat_info = pandas.read_json(
        json.dumps(cat_info)).drop_duplicates(
        ['key'])
    cat_keys = cat_info['key'].tolist()
    keys = []
    for k in cat_keys:
        key = {}
        key['key'] = k
        keys.append(key)
    profit_list = await dynamoDB_app.async_batch_get_item('profit', keys)
    if len(profit_list) == 0:
        return []
    cat_profit = pandas.read_json(json.dumps(profit_list))
    profit_data = pandas.merge(cat_info, cat_profit)
    profit_data = profit_data.drop_duplicates(['key'])
    cat_profit_df = profit_data.groupby(['cat_id',
                                         'cat_name'],
                                        as_index=False). \
        agg({'value': numpy.sum})
    return cat_profit_df


async def get_data(cat_info, cat_last_info):
    cat_sales = await get_sales(cat_info)
    cat_last_week_sales = await get_sales(cat_last_info)
    cat_profit = await get_profit(cat_info)
    cat_last_week_profit = await get_profit(cat_last_info)
    if len(cat_sales) == 0 or len(cat_last_week_sales) == 0 or len(
            cat_profit) == 0 or len(cat_last_week_profit) == 0:
        return []
    cat_sales = pandas.merge(
        cat_sales,
        cat_last_week_sales,
        on='cat_id')
    cat_profit = pandas.merge(cat_profit, cat_last_week_profit,
                              on='cat_id')
    cat_data = pandas.merge(cat_sales, cat_profit, on='cat_id')
    cat_data['name'] = cat_data['cat_name_x_x']
    cat_data['sales'] = cat_data['value_x_x']
    cat_data['last_week_sales'] = cat_data['value_y_x']
    cat_data['rate'] = cat_data[['value_x_x', 'value_x_y']].apply(
        lambda x: _calculate_profit_rote(*x), axis=1
    )
    cat_data['last_week_rate'] = cat_data[
        ['value_y_x', 'value_y_y']].apply(
        lambda x: _calculate_profit_rote(*x), axis=1
    )
    cat_data = cat_data[cat_data['rate'] <= 99]
    cat_data = cat_data[cat_data['last_week_rate'] <= 99]
    cat_data.sort_values(
        by=['sales', 'cat_id', 'rate'],
        ascending=[0, 1, 0],
        inplace=True)
    cat_data = cat_data[['cat_id',
                         'name',
                         'sales',
                         'last_week_sales',
                         'rate',
                         'last_week_rate']].to_dict('records')
    return cat_data


class SunFigureHandler(BaseHandler):

    @standard_api
    @login_required
    async def get(self):
        user = await self.get_current_user()
        start_time = self.get_argument('start_time')
        end_time = self.get_argument('end_time')
        store_id = self.get_argument('store_id')
        cm_id, foreign_store_id = await dus.get_store_info(user, store_id)
        category = await manager.execute(Category.select().where(
            Category.cm_id == cm_id
        ))
        dates = tus.dateline(start_time, end_time)
        cat_info = []
        for cat in category:
            flag = False
            cat_l1 = cat.foreign_category_lv1
            cat_l2 = cat.foreign_category_lv2
            cat_l3 = cat.foreign_category_lv3
            cat_l4 = cat.foreign_category_lv4
            if cat.level == 1:
                cat_id = cat_l1
            elif cat.level == 2:
                flag = True
                cat_id = cat_l2
            elif cat.level == 3:
                flag = True
                cat_id = cat_l3
            elif cat.level == 4:
                flag = True
                cat_id = cat_l4
            for date in dates:
                date = to_str(date, '%Y-%m-%d')
                cat_dict = {}
                cat_dict['cat_l1_id'] = cat_l1
                cat_dict['cat_l1_name'] = cat.foreign_category_lv1_name
                if flag:
                    cat_dict['cat_l2_id'] = cat_l2
                    cat_dict['cat_l2_name'] = cat.foreign_category_lv2_name
                else:
                    cat_dict['cat_l2_id'] = cat_l1
                    cat_dict['cat_l2_name'] = cat.foreign_category_lv1_name
                cat_dict['key'] = \
                    f'day:cat:{cm_id}:{foreign_store_id}:{cat_id}:{date}'
                cat_info.append(cat_dict)
        response = {}
        cat_info = pandas.read_json(
            json.dumps(cat_info)).drop_duplicates(
            ['key'])
        cat_keys = cat_info['key'].tolist()
        keys = []
        for k in cat_keys:
            key = {}
            key['key'] = k
            keys.append(key)
        cat_l1_sales, cat_l2_sales = await get_cat_sales(cat_info, keys)
        cat_l1_profit, cat_l2_profit = await get_cat_profit(cat_info, keys)
        response['cat_l1_sales'] = cat_l1_sales
        response['cat_l2_sales'] = cat_l2_sales
        response['cat_l1_profit'] = cat_l1_profit
        response['cat_l2_profit'] = cat_l2_profit
        return {
            'data': response
        }


class SalesDiffHandler(BaseHandler):

    @standard_api
    @login_required
    async def get(self):
        user = await self.get_current_user()
        start_time = self.get_argument('start_time')
        end_time = self.get_argument('end_time')
        store_id = self.get_argument('store_id')
        cm_id, foreign_store_id = await dus.get_store_info(user, store_id)
        category = await manager.execute(Category.select().where(
            Category.cm_id == cm_id
        ))
        last_monday, last_sunday = tus.get_last_week(start_time)
        dates = tus.dateline(start_time, end_time)
        last_dates = tus.dateline(last_monday, last_sunday)
        cat_l2_info = []
        cat_l3_info = []
        cat_l2_last_info = []
        cat_l3_last_info = []
        for cat in category:
            cat_l2 = cat.foreign_category_lv2
            cat_l3 = cat.foreign_category_lv3
            if cat_l2 == '' or cat_l2 is None:
                continue
            for date in dates:
                date = to_str(date, '%Y-%m-%d')
                cat_dict = {}
                cat_dict['cat_id'] = cat_l2
                cat_dict['cat_name'] = cat.foreign_category_lv2_name
                cat_dict['key'] = \
                    f'day:cat:{cm_id}:{foreign_store_id}:{cat_l2}:{date}'
                cat_l2_info.append(cat_dict)
                cat_dict = {}
                cat_dict['cat_id'] = cat_l3
                cat_dict['cat_name'] = cat.foreign_category_lv3_name
                cat_dict['key'] = \
                    f'day:cat:{cm_id}:{foreign_store_id}:{cat_l3}:{date}'
                cat_l3_info.append(cat_dict)
            for date in last_dates:
                date = to_str(date, '%Y-%m-%d')
                cat_dict = {}
                cat_dict['cat_id'] = cat_l2
                cat_dict['cat_name'] = cat.foreign_category_lv2_name
                cat_dict['key'] = \
                    f'day:cat:{cm_id}:{foreign_store_id}:{cat_l2}:{date}'
                cat_l2_last_info.append(cat_dict)
                cat_dict = {}
                cat_dict['cat_id'] = cat_l3
                cat_dict['cat_name'] = cat.foreign_category_lv3_name
                cat_dict['key'] = \
                    f'day:cat:{cm_id}:{foreign_store_id}:{cat_l3}:{date}'
                cat_l3_last_info.append(cat_dict)
        cat_l2_data = await get_data(cat_l2_info, cat_l2_last_info)
        cat_l3_data = await get_data(cat_l3_info, cat_l3_last_info)
        response = {}
        response['cat_l2_data'] = cat_l2_data
        response['cat_l3_data'] = cat_l3_data
        return {'data': response}
