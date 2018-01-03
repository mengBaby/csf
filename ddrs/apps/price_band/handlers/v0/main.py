import json
import datetime
from collections import OrderedDict
from uvtor.core.decorators.api import standard_api
from uvtor.db.models import manager
from utils.ddrs_utils import get_store_info
from uvtor.conf import settings
from consts import ITEMS
from apps.price_band.handlers import BaseHandler
from models.model import Store, Category, \
    UserArea, ChainUser, StoreArea, UserStore, Area
from utils import ddrs_utils as dus


class PriceBandHandler(BaseHandler):
    @standard_api
    async def get(self):
        start_date = self.get_argument('start_date')
        end_date = self.get_argument('end_date')
        cat_id = self.get_argument('cat_id')
        store_id = self.get_argument('store_id')
        cat_id = ':'.join(json.loads(cat_id))
        user = await self.get_current_user()
        cm_id, foreign_store_id = await get_store_info(user, store_id)
        # 获取三周数据

        first_start, first_end, second_start, second_end = get_three_week(
            start_date, end_date)
        period_third = start_date + ':' + end_date
        period_second = second_start + ':' + second_end
        period_first = first_start + ':' + first_end

        price_key_first = str(cm_id) + ':' + foreign_store_id + \
            ':price_band:' + cat_id + ':' + period_first
        price_key_second = str(cm_id) + ':' + foreign_store_id + \
            ':price_band:' + cat_id + ':' + period_second
        price_key_third = str(cm_id) + ':' + foreign_store_id + \
            ':price_band:' + cat_id + ':' + period_third

        first_res = await settings.dynamoDB_app.async_get_item(
            ITEMS, {
                'key': price_key_first
            })
        second_res = await settings.dynamoDB_app.async_get_item(
            ITEMS, {
                'key': price_key_second
            })
        third_res = await settings.dynamoDB_app.async_get_item(
            ITEMS, {
                'key': price_key_third
            })

        three_data = {
            'first_data': json.loads(first_res['value']) if first_res else [],
            'second_data': json.loads(second_res['value'])
            if second_res else [],
            'third_data': json.loads(third_res['value']) if third_res else [],
        }

        data = transform_three_data(three_data)

        sku_key = str(cm_id) + ':' + foreign_store_id + ':sku:' + \
            cat_id + ':' + period_first
        _key = {'key': sku_key}
        sku_res = await settings.dynamoDB_app.async_get_item(ITEMS, _key)
        print(sku_res)
        res = {'price_band': data, 'sku': []}
        if sku_res:
            res['sku'] = json.loads(
                sku_res['value']) if sku_res['value'] else []

        return {'data': res}


class CategoryHandler(BaseHandler):
    @standard_api
    async def get(self):
        store_id = self.get_argument('store_id')
        user = await self.get_current_user()
        cm_id, foreign_store_id = await get_store_info(user, store_id)
        # cm_id = 1001
        categories = await manager.execute(
            Category.select().where(Category.cm_id == cm_id))
        level = Category.select(
            Category.level).where(Category.cm_id == cm_id).order_by(
                Category.level.desc()).first()
        cat = ''
        print(level.level)
        if level.level == 2:
            cat = dus.gen_category_lv2(categories)
        elif level.level == 3:
            cat = dus.gen_category_lv3(categories)
        elif level.level == 4:
            cat = dus.gen_category_lv4(categories)
        return {'data': cat}


def get_three_week(start, end):
    three_sunday = datetime.datetime.strptime(end, '%Y-%m-%d')
    three_monday = datetime.datetime.strptime(start, '%Y-%m-%d')
    second_monday = three_monday - datetime.timedelta(weeks=1)
    second_sunday = three_monday - datetime.timedelta(days=1)
    first_monday = second_monday - datetime.timedelta(weeks=1)
    first_sunday = second_monday - datetime.timedelta(days=1)
    second_start = second_monday.strftime('%Y-%m-%d')
    second_end = second_sunday.strftime('%Y-%m-%d')
    first_start = first_monday.strftime('%Y-%m-%d')
    first_end = first_sunday.strftime('%Y-%m-%d')
    return first_start, first_end, second_start, second_end


def transform_cat_list(data):
    """
    价格带中获取三周数据，因某些物品可能某周没有数据，
    所以在这里处理一下找到三周的数据。
    返回的是三周卖出去的所有的物品的组成的字典
    这里可以打Log 看一下结构就明白了
    :param data:
    :return:
    """
    item_list = []
    if data['first_data']:
        for item in data['first_data']['item_id']:
            if item not in item_list:
                item_list.append(item)
    if data['second_data']:
        for item in data['second_data']['item_id']:
            if item not in item_list:
                item_list.append(item)
    if data['third_data']:
        for item in data['third_data']['item_id']:
            if item not in item_list:
                item_list.append(item)
    cat_list = OrderedDict()
    temp_dict = {'sales': 0, 'sales_volume': 0, 'profit': 0}
    for i in item_list:
        cat_list[i] = OrderedDict(
            first_data=temp_dict,
            second_data=temp_dict,
            third_data=temp_dict,
            price=None,
            item_name=None)

    return cat_list


def transform_three_data(data):
    cat_list = transform_cat_list(data)
    if data['first_data']:
        for item in data['first_data']['item_id']:
            if item in cat_list:
                item_price = data['first_data']['price'].pop(0)
                item_name = data['first_data']['item_name'].pop(0)
                temp_data = {
                    "profit": data['first_data']['profit'].pop(0),
                    "sales_volume": data['first_data']['sales_volume'].pop(0),
                    "price": item_price
                }
                cat_list[item]['first_data'] = temp_data
                cat_list[item]['price'] = item_price
                cat_list[item]['item_name'] = item_name
    if data['second_data']:
        for item in data['second_data']['item_id']:
            if item in cat_list:
                item_price = data['second_data']['price'].pop(0)
                item_name = data['second_data']['item_name'].pop(0)
                temp_data = {
                    "profit": data['second_data']['profit'].pop(0),
                    "sales_volume": data['second_data']['sales_volume'].pop(0),
                    "price": item_price
                }
                cat_list[item]['second_data'] = temp_data
                if cat_list[item]['price'] is None:
                    cat_list[item]['price'] = item_price
                cat_list[item]['item_name'] = item_name
    if data['third_data']:
        for item in data['third_data']['item_id']:
            if item in cat_list:
                item_price = data['third_data']['price'].pop(0)
                item_name = data['third_data']['item_name'].pop(0)
                temp_data = {
                    "profit": data['third_data']['profit'].pop(0),
                    "sales_volume": data['third_data']['sales_volume'].pop(0),
                    "price": item_price
                }
                cat_list[item]['third_data'] = temp_data
                if cat_list[item]['price'] is None:
                    cat_list[item]['price'] = item_price
                cat_list[item]['item_name'] = item_name

    cat_list = sorted(
        cat_list.items(), key=lambda ele: ele[1]['price'], reverse=True)
    cat_list = sort_price_band_third_week(cat_list)
    return cat_list


def sort_price_band_third_week(data):
    """
    与 transform_cat_list 配合使用 排序
    :param data:
    :return:
    """
    cat_list = []
    for item in data:
        cat_list.append(item[1])
    return cat_list
