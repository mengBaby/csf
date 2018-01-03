from uvtor.core.decorators.api import standard_api
from utilib.utils.timezone import to_str
from uvtor.core import settings
from apps.ring_analysis.handlers import BaseHandler
from uvtor.db.models import manager
from models.model import Category
from utils.auth import login_required
from utils import ddrs_utils as dus
from utils import time_utils as tus
import datetime
import pandas
import json
import numpy

dynamoDB_app = settings.dynamoDB_app


async def get_thirteen_weeks_data(
        cm_id, foreign_store_id, table_name, year_start, cat_id):
    start_monday, last_sunday = tus.get_thirteen_week_day(year_start)[:2]
    dateline = pandas.date_range(start_monday, last_sunday)
    keys = []
    for date in dateline:
        date = to_str(date, '%Y-%m-%d')
        key = {}
        key['key'] = f'day:cat:{cm_id}:{foreign_store_id}:{cat_id}:{date}'
        keys.append(key)
    sales = await dynamoDB_app.async_batch_get_item(table_name, keys)
    if not sales:
        return []
    sales = pandas.read_json(json.dumps(sales))
    keys = pandas.read_json(json.dumps(keys))
    sales = pandas.merge(sales, keys, how='right').fillna(0)
    sales.sort_values(
        by=['key'],
        ascending=[1],
        inplace=True
    )
    sales = sales['value'].tolist()
    data = []
    sum = 0
    for i in range(len(sales)):
        sum += sales[i]
        if i != 0 and (i + 1) % 7 == 0:
            data.append(sum)
            sum = 0
    return data


def get_keys(cm_id, foreign_store_id, year, cat_id):
    keys = []
    sales_info = []
    i = 1
    while i <= 12:
        first_day, last_day = tus.get_month_day(year, i)
        info = {}
        k = f'month:cat:{cm_id}:{foreign_store_id}' \
            f':{cat_id}:{first_day}:{last_day}'
        info['year'] = year
        info['month'] = i
        info['key'] = k
        key = {}
        key['key'] = k
        keys.append(key)
        sales_info.append(info)
        i += 1
    return keys, sales_info


async def get_month_data(cm_id, foreign_store_id, cat_id):
    now = datetime.datetime.now()
    this_year = now.year
    last_year = this_year - 1
    last_year_keys, last_year_sales_info = \
        get_keys(cm_id, foreign_store_id, last_year, cat_id)
    year_keys, year_sales_info = \
        get_keys(cm_id, foreign_store_id, this_year, cat_id)
    keys = year_keys + last_year_keys
    sales_info = last_year_sales_info + year_sales_info
    sales = await dynamoDB_app.async_batch_get_item('sales', keys)
    if not sales:
        return []
    sales = pandas.read_json(json.dumps(sales))
    sales_info = pandas.read_json(
        json.dumps(sales_info)).drop_duplicates(
        ['key'])
    sales = pandas.merge(
        sales,
        sales_info, how='right').fillna(0)
    sales.sort_values(
        by=['year', 'month'],
        ascending=[1, 1],
        inplace=True)
    sales = sales['value'].tolist()
    return sales


async def get_current_month_sales(cm_id,
                                  foreign_store_id,
                                  cat_id,
                                  year,
                                  month,
                                  day):
    j = 1
    keys = []
    while j <= day:
        key = {}
        if j < 10:
            key['key'] = f'day:cat:{cm_id}:{foreign_store_id}:{cat_id}:' \
                f'{year}-{month}-0{j}'
        else:
            key['key'] = f'day:cat:{cm_id}:{foreign_store_id}:{cat_id}:' \
                f'{year}-{month}-{j}'
        j += 1
        keys.append(key)
    sales = await dynamoDB_app.async_batch_get_item('sales', keys)
    if sales:
        sales = pandas.read_json(json.dumps(sales))
        sales = sales.agg({'value': numpy.sum})
        return sales['value']
    return 0


class ThirteenWeeksSalesHandler(BaseHandler):
    @standard_api
    @login_required
    async def get(self):
        user = await self.get_current_user()
        store_id = self.get_argument('store_id')
        cat_ids = json.loads(self.get_argument('cat_ids'))
        cat_names = json.loads(self.get_argument('cat_names'))
        cm_id, foreign_store_id = await dus.get_store_info(user, store_id)
        now = datetime.datetime.now()
        last_year_start = datetime.date(now.year - 1, 1, 1)
        last_year_start += datetime.timedelta(7 - last_year_start.weekday())
        this_year_start = datetime.date(now.year, 1, 1)
        this_year_start += datetime.timedelta(7 - this_year_start.weekday())
        response = {}
        last_sunday, last_monday = tus.get_thirteen_week_day(this_year_start)[
            1:]
        response['date'] = f'{last_monday}~{last_sunday}'
        response['cat_weeks_sales'] = {}
        cat_info = {}
        if not cat_ids:
            cats = await manager.execute(
                Category.select(
                    Category.foreign_category_lv1,
                    Category.foreign_category_lv1_name,
                ).distinct(Category.foreign_category_lv1).where(
                    Category.cm_id == cm_id
                ))
            for cat in cats:
                cat_info[cat.foreign_category_lv1] = {}
                cat_info[cat.foreign_category_lv1]['name'] = \
                    cat.foreign_category_lv1_name
        else:
            for i in range(len(cat_ids)):
                cat_info[cat_ids[i]] = {}
                cat_info[cat_ids[i]]['name'] = cat_names[i]
        del_ids = []
        for cat_id in cat_info:
            sales = await get_thirteen_weeks_data(
                cm_id, foreign_store_id, 'sales', this_year_start, cat_id)
            cat_info[cat_id]['sales'] = sales
            cat_info[cat_id]['max'] = 0
            if sales:
                cat_info[cat_id]['max'] = max(sales)
            else:
                del_ids.append(cat_id)
        for id in del_ids:
            del cat_info[id]

        response['cat_weeks_sales'] = cat_info
        return {
            'data': response
        }


class MonthSalesHandler(BaseHandler):
    @standard_api
    @login_required
    async def get(self):
        user = await self.get_current_user()
        store_id = self.get_argument('store_id')
        cat_ids = json.loads(self.get_argument('cat_ids'))
        cat_names = json.loads(self.get_argument('cat_names'))
        cm_id, foreign_store_id = await dus.get_store_info(user, store_id)
        now = datetime.datetime.now()
        response = {}
        response['date'] = str(now)[:10]
        response['sales'] = {}
        cat_info = {}
        if not cat_ids:
            cats = await manager.execute(
                Category.select(
                    Category.foreign_category_lv1,
                    Category.foreign_category_lv1_name,
                ).distinct(Category.foreign_category_lv1).where(
                    Category.cm_id == cm_id
                ))
            for cat in cats:
                cat_info[cat.foreign_category_lv1] = {}
                cat_info[cat.foreign_category_lv1]['name'] = \
                    cat.foreign_category_lv1_name
        else:
            for i in range(len(cat_ids)):
                cat_info[cat_ids[i]] = {}
                cat_info[cat_ids[i]]['name'] = cat_names[i]
        del_ids = []
        for cat_id in cat_info:
            sales = await get_month_data(cm_id, foreign_store_id, cat_id)
            if sales:
                cat_info[cat_id]['last_year_sales'] = sales[:12]
                cat_info[cat_id]['this_year_sales'] = sales[12:]
                year = now.year
                month = now.month
                day = now.day
                current_month_sales = await get_current_month_sales(
                    cm_id,
                    foreign_store_id,
                    cat_id,
                    year,
                    month,
                    day)
                cat_info[cat_id]['this_year_sales'][month -
                                                    1] = current_month_sales
            else:
                del_ids.append(cat_id)
        for id in del_ids:
            del cat_info[id]
        response['sales'] = cat_info
        return {
            'data': response
        }
