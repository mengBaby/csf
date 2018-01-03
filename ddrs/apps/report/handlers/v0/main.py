from uvtor.core.decorators.api import standard_api
from apps.report.handlers import BaseHandler
from models.model import Store, UserStore
from uvtor.db.models import manager
from utilib.utils.timezone import to_str
from uvtor.core import settings
from utils.auth import login_required
import json
import pandas
import numpy

dynamoDB_app = settings.dynamoDB_app


def get_data(data, first_col):
    response = []
    if first_col == 'store':
        summary_key = 'store_name'
        detail_key = 'date'
    else:
        detail_key = 'store_name'
        summary_key = 'date'
    summary = data.groupby([summary_key], as_index=False).agg(
        {'sales': numpy.sum,
         'traffic': numpy.sum,
         'sales_volume': numpy.sum
         }
    )
    for i in range(len(summary)):
        dict = {}
        dict['title'] = str(summary[summary_key][i])
        dict['sales_sum'] = format(summary['sales'][i], '0.1f')
        dict['traffic_sum'] = int(summary['traffic'][i])
        dict['sales_volume_sum'] = format(
            summary['sales_volume'][i], '0.1f')
        dict['details'] = []
        store_data = data[data[summary_key] ==
                          summary[summary_key][i]]
        store_data.sort_values(
            by=['date', 'sales'], ascending=[1, 0], inplace=True)
        store_data = store_data.reset_index(drop=True)
        for j in range(len(store_data)):
            detail = {}
            detail['title'] = str(store_data[detail_key][j])
            detail['sales'] = format(store_data['sales'][j], '0.1f')
            detail['traffic'] = int(store_data['traffic'][j])
            detail['sales_volume'] = format(
                store_data['sales_volume'][j], '0.1f')
            dict['details'].append(detail)
        response.append(dict)
    return response


class ReportHandler(BaseHandler):

    @standard_api
    @login_required
    async def get(self):
        user = await self.get_current_user()
        if user.is_superuser:
            user = self.get_cookie('userId')
        store_ids = json.loads(self.get_argument('store_ids'))
        if len(store_ids) == 0:
            store_ids = []
            user_stores = UserStore.select().where(
                UserStore.user == user)
            for user_store in user_stores:
                store_ids.append(user_store.store.id)
        start_time = self.get_argument('start_time', None)
        end_time = self.get_argument('end_time', None)
        first_col = self.get_argument('first_col', None)

        dates = pandas.date_range(start_time, end_time)
        response = []
        keys = []
        infos = []
        for store_id in store_ids:
            store = await manager.get(
                Store.select().where(
                    Store.id == store_id
                )
            )
            store_name = store.store_name
            cm_id = store.cm_id
            foreign_store_id = store.foreign_store_id
            for date in dates:
                key = {}
                date = to_str(date, '%Y-%m-%d')
                k = f'day:{cm_id}:{foreign_store_id}:{date}'
                key['key'] = k
                info = {}
                info['store_name'] = store_name
                info['date'] = date
                info['key'] = k
                keys.append(key)
                infos.append(info)
        sales = await dynamoDB_app.async_batch_get_item('sales', keys)
        traffic = await dynamoDB_app.async_batch_get_item('traffic', keys)
        sales_volume = await dynamoDB_app.async_batch_get_item(
            'sales_volumes', keys)
        if sales and traffic and sales_volume:
            sales = pandas.read_json(json.dumps(sales))
            traffic = pandas.read_json(json.dumps(traffic))
            sales_volume = pandas.read_json(json.dumps(sales_volume))
            infos = pandas.read_json(json.dumps(infos))
            sales['sales'] = sales['value']
            traffic['traffic'] = traffic['value']
            sales_volume['sales_volume'] = sales_volume['value']
            data = pandas.merge(sales, infos, how='right').fillna(0)
            del data['value']
            data = pandas.merge(traffic, data, how='right').fillna(0)
            del data['value']
            data = pandas.merge(sales_volume, data, how='right').fillna(0)
        else:
            return {
                'data': response
            }
        response = get_data(data, first_col)
        return {
            'data': response
        }
