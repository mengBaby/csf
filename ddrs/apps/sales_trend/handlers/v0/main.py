from uvtor.core.decorators.api import standard_api
from utilib.utils.timezone import to_str
from uvtor.core import settings
from apps.ring_analysis.handlers import BaseHandler
from utils.auth import login_required
from utils import ddrs_utils as dus
from utils import time_utils as tus
import datetime
import pandas
import json
import numpy

dynamoDB_app = settings.dynamoDB_app


async def get_thirteen_weeks_data(
        cm_id, foreign_store_id, table_name, year_start):
    start_monday, last_sunday = tus.get_thirteen_week_day(year_start)[:2]
    dateline = pandas.date_range(start_monday, last_sunday)
    keys = []
    for date in dateline:
        date = to_str(date, '%Y-%m-%d')
        key = {}
        key['key'] = f'day:{cm_id}:{foreign_store_id}:{date}'
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
    if table_name == 'sales':
        sales['value'] = sales['value'] / 10000
    sales = sales['value'].tolist()
    data = []
    sum = 0
    for i in range(len(sales)):
        sum += sales[i]
        if i != 0 and (i + 1) % 7 == 0:
            data.append(sum)
            sum = 0
    return data


async def get_current_month_sales(cm_id, foreign_store_id, year, month, day):
    j = 1
    keys = []
    while j <= day:
        key = {}
        if j < 10:
            key['key'] = f'day:{cm_id}:{foreign_store_id}:{year}-{month}-0{j}'
        else:
            key['key'] = f'day:{cm_id}:{foreign_store_id}:{year}-{month}-{j}'
        j += 1
        keys.append(key)
    sales = await dynamoDB_app.async_batch_get_item('sales', keys)
    if sales:
        sales = pandas.read_json(json.dumps(sales))
        sales = sales.agg({'value': numpy.sum})
        return sales['value'] / 10000
    return 0


class YearSalesHandler(BaseHandler):

    @standard_api
    @login_required
    async def get(self):
        user = await self.get_current_user()
        store_id = self.get_argument('store_id')
        cm_id, foreign_store_id = await dus.get_store_info(user, store_id)
        now = datetime.datetime.now()
        this_year = now.year
        last_year = this_year - 1
        i = 1
        keys = []
        sales_info = []
        response = {}
        response['last_year_sales'] = []
        response['this_year_sales'] = []
        while i <= 12:
            first_day, last_day = tus.get_month_day(last_year, i)
            info = {}
            k = f'month:{cm_id}:{foreign_store_id}:{first_day}:{last_day}'
            info['year'] = last_year
            info['month'] = i
            info['key'] = k
            key = {}
            key['key'] = k
            keys.append(key)
            sales_info.append(info)
            first_day, last_day = tus.get_month_day(this_year, i)
            info = {}
            k = f'month:{cm_id}:{foreign_store_id}:{first_day}:{last_day}'
            info['year'] = this_year
            info['month'] = i
            info['key'] = k
            key = {}
            key['key'] = k
            keys.append(key)
            sales_info.append(info)
            i += 1
        year_sales = await dynamoDB_app.async_batch_get_item('sales', keys)
        if not year_sales:
            return {
                'data': response
            }
        year_sales = pandas.read_json(json.dumps(year_sales))
        sales_info = pandas.read_json(
            json.dumps(sales_info)).drop_duplicates(
            ['key'])
        year_sales = pandas.merge(
            year_sales,
            sales_info, how='right').fillna(0)
        year_sales.sort_values(
            by=['year', 'month'],
            ascending=[1, 1],
            inplace=True)
        year_sales['value'] = year_sales['value'] / 10000
        year_sales = year_sales['value'].tolist()
        response['last_year_sales'] = year_sales[:12]
        response['this_year_sales'] = year_sales[12:]
        month = now.month
        day = now.day
        current_month_sales = await get_current_month_sales(cm_id,
                                                            foreign_store_id,
                                                            this_year,
                                                            month,
                                                            day)
        response['this_year_sales'][month - 1] = current_month_sales
        return {
            'data': response
        }


class ThirteenWeeksSalesHandler(BaseHandler):
    @standard_api
    @login_required
    async def get(self):
        user = await self.get_current_user()
        store_id = self.get_argument('store_id')
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
        this_year_weeks_sales = await get_thirteen_weeks_data(
            cm_id, foreign_store_id, 'sales', this_year_start)
        last_year_weeks_sales = await get_thirteen_weeks_data(
            cm_id, foreign_store_id, 'sales', last_year_start)
        this_year_weeks_traffic = await get_thirteen_weeks_data(
            cm_id, foreign_store_id, 'traffic', this_year_start)
        response['this_year_thirteen_weeks_sales'] = this_year_weeks_sales
        response['last_year_thirteen_weeks_sales'] = last_year_weeks_sales
        response['this_year_thirteen_weeks_traffic'] = this_year_weeks_traffic
        if this_year_weeks_sales and this_year_weeks_traffic:
            dict = {}
            dict['sales'] = this_year_weeks_sales
            dict['traffic'] = this_year_weeks_traffic
            df = pandas.read_json(json.dumps(dict))
            avg_price = df['sales'] * 10000 / df['traffic']
            avg_price = avg_price.fillna(0)
            response['this_year_thirteen_weeks_avg_price'] = \
                avg_price.tolist()
        else:
            response['this_year_thirteen_weeks_avg_price'] = []
        return {
            'data': response
        }
