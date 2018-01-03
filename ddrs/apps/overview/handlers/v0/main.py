import datetime
import json
from decimal import Decimal
from uvtor.db.models import manager
from playhouse.shortcuts import model_to_dict
from utilib.utils.dynamo import DynamoDBHelper
from uvtor.core.decorators.api import standard_api
from apps.overview.handlers import BaseHandler
from uvtor.conf import settings
from models.model import Store, Category, \
    UserArea, ChainUser, StoreArea, UserStore, Area
from utils import ddrs_utils as dus

TABLE_NAME = ['sales', 'profit', 'traffic']


class OverviewHandler(BaseHandler):
    @standard_api
    async def get(self):
        start_date = self.get_argument('start_date')
        end_date = self.get_argument('end_date')
        cat_id = self.get_argument('cat_id')
        area = self.get_argument('area_id')
        latitude = self.get_argument('latitude')
        reference = self.get_argument('reference')
        store_type = self.get_argument('store_type')
        user = await self.get_current_user()
        chain_user = await manager.get(
            ChainUser.select().where(ChainUser.user == user))
        # print(self.request.arguments)

        # 循环计算
        area = json.loads(area)
        area_length = len(area)
        cat_id = json.loads(cat_id)

        if area_length == 1 and (area[0] == '0' or area[0] == 0):

            store_list = Store.select().join(UserStore).where(
                Store.chain_store == chain_user.chain_store,
                Store.store_type == store_type, UserStore.user == user.id)
        else:

            store_list = Store.select().join(StoreArea).where(
                Store.chain_store == chain_user.chain_store,
                Store.store_type == store_type, StoreArea.area << area)
        store_data = {}
        store_address = {}
        length = len(cat_id)
        for store in store_list:
            if (cat_id[0] == '0' or cat_id[0] == 0) and length == 1:
                key = 'day:' + str(
                    store.cm_id) + ':' + store.foreign_store_id + ':'
                keys = gen_key(key, start_date, end_date)
            else:
                key = 'day:cat:' + str(
                    store.cm_id) + ':' + store.foreign_store_id + ':'
                temp_key = gen_key_v2(cat_id, key, start_date, end_date)
                keys = temp_key

            store_res = await settings.dynamoDB_app.async_batch_get_item(
                latitude, keys)
            store_data[store.store_name] = float(
                sum(Decimal(v['value']) for v in store_res))
            store_address[store.store_name] = [store.lng, store.lat]

            # 平均值
        if len(store_data) == 0:
            flag_value = 0
        else:
            flag_value = round(
                sum(i for i in store_data.values()) / len(store_data), 2)

        top_data = []
        other_data = []
        for k, v in store_data.items():
            if v > flag_value:
                lng = 0
                lat = 0
                if store_address[k][0]:
                    lng = float(store_address[k][0])
                if store_address[k][1]:
                    lat = float(store_address[k][1])

                temp = {'name': k, 'value': v, 'lng': lng, 'lat': lat}
                top_data.append(temp)
            else:
                lng = 0
                lat = 0
                if store_address[k][0]:
                    lng = float(store_address[k][0])
                if store_address[k][1]:
                    lat = float(store_address[k][1])

                temp = {'name': k, 'value': v, 'lng': lng, 'lat': lat}
                other_data.append(temp)
        if int(reference) == 2:
            length = round(len(top_data) * 0.2)
            temp_data = top_data[:length]
            other_data = top_data[length:] + other_data
            top_data = temp_data

        res = {
            'top_data': top_data,
            'other_data': other_data,
            'reference': flag_value,
            'start_date': start_date,
            'end_date': end_date
        }

        return {'data': res}


class OverViewBottomHandler(BaseHandler):
    @standard_api
    async def get(self):
        start_date = self.get_argument('start_date')
        end_date = self.get_argument('end_date')
        cat_id = self.get_argument('cat_id')
        end = datetime.datetime.today()
        area = self.get_argument('area_id')
        store_type = self.get_argument('store_type')
        diff = end.month - 3
        if diff < 10:
            start = str(end.year) + '-0' + str(diff) + '-01'
            end = end.strftime('%Y-%m-%d')
        else:
            start = str(end.year) + '-' + str(diff) + '-01'
            end = end.strftime('%Y-%m-%d')

        user = await self.get_current_user()
        chain_user = await manager.get(
            ChainUser.select().where(ChainUser.user == user))

        area = json.loads(area)
        area_length = len(area)
        cat_id = json.loads(cat_id)
        if area_length == 1 and (area[0] == '0' or area[0] == 0):
            store_list = Store.select().join(UserStore).where(
                Store.chain_store == chain_user.chain_store,
                Store.store_type == store_type, UserStore.user == user.id)
        else:
            store_list = Store.select().join(StoreArea).where(
                Store.chain_store == chain_user.chain_store,
                Store.store_type == store_type, StoreArea.area << area)
        sales = gen_date_dict(start, end)
        profit = gen_date_dict(start, end)
        traffic = gen_date_dict(start, end)
        all_keys = []
        length = len(cat_id)
        for store in store_list:
            if (cat_id[0] == '0' or cat_id[0] == 0) and length == 1:
                key = 'day:' + str(
                    store.cm_id) + ':' + store.foreign_store_id + ':'
                all_keys += gen_key(key, start, end)
            else:
                key = 'day:cat:' + str(
                    store.cm_id) + ':' + store.foreign_store_id + ':'
                temp_key = gen_key_v2(cat_id, key, start, end)
                all_keys += temp_key
        sales_res = await settings.dynamoDB_app.async_batch_get_item(
            'sales', all_keys)
        for i in sales_res:
            sales[i['key'].split(':')[-1]] += float(i['value'])

        sales = tuple_to_dict(
            sorted(sales.items(), key=lambda item: item[1], reverse=True))

        profit_res = await settings.dynamoDB_app.async_batch_get_item(
            'profit', all_keys)
        for i in profit_res:
            profit[i['key'].split(':')[-1]] += float(i['value'])

        profit = tuple_to_dict(
            sorted(profit.items(), key=lambda item: item[1], reverse=True))

        traffic_res = await settings.dynamoDB_app.async_batch_get_item(
            'traffic', all_keys)
        for i in traffic_res:
            traffic[i['key'].split(':')[-1]] += float(i['value'])

        traffic = tuple_to_dict(
            sorted(traffic.items(), key=lambda item: item[1], reverse=True))
        last_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        next_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        length = int((next_date - last_date).days) + 1
        res_sales = sum_data(sales, start_date, end_date)
        res_profit = sum_data(profit, start_date, end_date)
        res_traffic = sum_data(traffic, start_date, end_date)
        if res_sales == 0:
            res_order = 0
        else:
            res_order = round(res_sales / res_traffic, 2)
        sales_max = sum(i for i in list(sales.values())[:length])
        profit_max = sum(i for i in list(profit.values())[:length])
        traffic_max = sum(i for i in list(traffic.values())[:length])
        data = {
            'sales': {
                'value': res_sales,
                'max': sales_max
            },
            'profit': {
                'value': res_profit,
                'max': profit_max
            },
            'traffic': {
                'value': res_traffic,
                'max': traffic_max
            },
            'order': {
                'value': res_order,
                'max': round(res_order * 1.25, 2)
            }
        }

        return {'data': data}


class CategoryHandler(BaseHandler):
    @standard_api
    async def get(self):
        user = await self.get_current_user()
        chain_user = await manager.get(
            ChainUser.select().where(ChainUser.user == user))
        store = await manager.get(
            Store.get(Store.chain_store == chain_user.chain_store))
        categories = await manager.execute(
            Category.select().where(Category.cm_id == store.cm_id))
        cat = dus.gen_category_v2(categories)
        return {'data': cat}


class AreaHandler(BaseHandler):
    @standard_api
    async def get(self):
        # 由用户获取区域
        user = await self.get_current_user()

        areas = await manager.execute(
            Area.select().join(UserArea).where(UserArea.user == user)
        )
        res = dus.gen_area(areas)

        return {'data': res}


def gen_category(data):
    """
    获取分类
    :param data:
    :return:
    """
    _cat = {}
    for i in data:
        key_lv1 = i.foreign_category_lv1
        key_lv2 = i.foreign_category_lv2
        key_lv3 = i.foreign_category_lv3
        key_lv4 = i.foreign_category_lv4

        if key_lv1 not in _cat:
            _cat[key_lv1] = {}
            _cat[key_lv1]['children'] = {}
        if len(key_lv1) != 0 and len(key_lv2) != 0:
            if key_lv2 not in _cat[key_lv1]['children']:
                _cat[key_lv1]['children'][key_lv2] = {}
                _cat[key_lv1]['children'][key_lv2]['children'] = {}
        if len(key_lv1) != 0 and len(key_lv2) != 0 and len(key_lv3) != 0:
            if key_lv3 not in _cat[key_lv1]['children'][key_lv2]['children']:

                _cat[key_lv1]['children'][key_lv2]['children'][key_lv3] = {}
                if i.foreign_category_lv1:
                    _cat[key_lv1]['id'] = i.foreign_category_lv1
                    _cat[key_lv1]['label'] = i.foreign_category_lv1_name

                if i.foreign_category_lv2:
                    _cat[key_lv1]['children'][key_lv2][
                        'id'] = i.foreign_category_lv2
                    _cat[key_lv1]['children'][key_lv2][
                        'label'] = i.foreign_category_lv2_name

                if i.foreign_category_lv3 and i.foreign_category_lv3 != '':
                    _cat[key_lv1]['children'][key_lv2]['children'][key_lv3][
                        'id'] = i.foreign_category_lv3
                    _cat[key_lv1]['children'][key_lv2]['children'][key_lv3][
                        'label'] = i.foreign_category_lv3_name

    return _cat


def gen_key(key, start_date, end_date):
    start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    keys = []
    while start <= end:
        _key = key + start.strftime('%Y-%m-%d')
        keys.append({'key': _key})
        start = start + datetime.timedelta(days=1)
    return keys


def gen_key_v2(cat_id, key, start_date, end_date):
    start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    keys = []
    while start <= end:
        for i in cat_id:
            _key = key + str(i) + ':' + start.strftime('%Y-%m-%d')
            keys.append({'key': _key})
        start = start + datetime.timedelta(days=1)
    return keys


def gen_date_dict(start_date, end_date):
    start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    _dict = {}
    while start <= end:
        _dict[start.strftime('%Y-%m-%d')] = 0
        start = start + datetime.timedelta(days=1)
    return _dict


def gen_area(data):
    """
    区域无限分级
    :param data:
    :return:
    """
    node_list = []
    entries = {}
    for i in data:

        entries[i.area.id] = entry = {
            'id': i.area.id,
            'pid': i.area.pid,
            'label': i.area.area_name,
            'is_end': i.area.is_end,
            'level': i.area.level,
        }
        if i.area.pid == 0 or i.area.pid not in entries:
            node_list.append(entry)
        else:
            parent = entries[i.area.pid]
            parent.setdefault('children', []).append(entry)

    return node_list


def transform_data(res, data):
    for i in data:
        res[i['key'].split(':')[-1]] += float(i['value'])
    return res


def sum_data(data, start_date, end_date):
    start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    res = 0

    while start <= end:
        res += Decimal(data[start.strftime('%Y-%m-%d')])
        start = start + datetime.timedelta(days=1)

    return round(float(res), 2)


def tuple_to_dict(data):
    _dict = {}
    for i in data:
        _dict[i[0]] = i[1]
    return _dict
