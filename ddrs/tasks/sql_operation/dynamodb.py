import asyncio
import boto3
import time
import pandas
import base64
import json
import datetime
from utilib.utils.dynamo import DynamoDBHelper
from uvtor.conf import settings
from models.model import Store
from consts import *
from tasks.sql_operation.select import Select
from tasks import celery_app
from utils.time_utils import get_month_last

# client = boto3.client('dynamodb')

dynamoDB_app = DynamoDBHelper(settings.AWS_ACCESS_KEY_ID,
                              settings.AWS_SECRET_ACCESS_KEY)


def create_table():

    # client.delete_table(TableName=SALES)
    # client.delete_table(TableName=PROFIT)
    # client.delete_table(TableName=TRAFFIC)
    # client.delete_table(TableName=ORDER)
    # client.delete_table(TableName=SALES_VOLUMES)
    # client.delete_table(TableName=ITEMS)
    dynamoDB_app.create_table(SALES, 'key', 'S')
    dynamoDB_app.create_table(PROFIT, 'key', 'S')
    dynamoDB_app.create_table(TRAFFIC, 'key', 'S')
    dynamoDB_app.create_table(ORDER, 'key', 'S')
    dynamoDB_app.create_table(SALES_VOLUMES, 'key', 'S')
    dynamoDB_app.create_table(ITEMS, 'key', 'S')

    return True


def save_day_data(cm_id, store_id, start, end):
    # 毛利润， 销售额， 单次
    data_dict = Select.select_store_day(cm_id, store_id, start, end)

    sales, profits, traffics, order_price, sales_volumes = get_day_items(
        cm_id, store_id, data_dict)
    batch_write_item.delay(SALES, sales)
    batch_write_item.delay(PROFIT, profits)
    batch_write_item.delay(TRAFFIC, traffics)
    batch_write_item.delay(ORDER, order_price)
    batch_write_item.delay(SALES_VOLUMES, sales_volumes)

    # 品类 毛利润， 销售额， 单次
    # lv1
    data_dict = Select.select_cat_lv1_day(cm_id, store_id, start, end)

    sales, profits, traffics, sales_volumes = get_day_cat_items(
        cm_id, store_id, data_dict)
    batch_write_item.delay(SALES, sales)
    batch_write_item.delay(PROFIT, profits)
    batch_write_item.delay(TRAFFIC, traffics)
    batch_write_item.delay(SALES_VOLUMES, sales_volumes)

    # lv2
    data_dict = Select.select_cat_lv2_day(cm_id, store_id, start, end)

    sales, profits, traffics, sales_volumes = get_day_cat_items(
        cm_id, store_id, data_dict)
    batch_write_item.delay(SALES, sales)
    batch_write_item.delay(PROFIT, profits)
    batch_write_item.delay(TRAFFIC, traffics)
    batch_write_item.delay(SALES_VOLUMES, sales_volumes)
    #
    # # lv3
    data_dict = Select.select_cat_lv3_day(cm_id, store_id, start, end)

    sales, profits, traffics, sales_volumes = get_day_cat_items(
        cm_id, store_id, data_dict)
    batch_write_item.delay(SALES, sales)
    batch_write_item.delay(PROFIT, profits)
    batch_write_item.delay(TRAFFIC, traffics)
    batch_write_item.delay(SALES_VOLUMES, sales_volumes)
    #
    # # lv4
    data_dict = Select.select_cat_lv4_day(cm_id, store_id, start, end)

    sales, profits, traffics, sales_volumes = get_day_cat_items(
        cm_id, store_id, data_dict)
    batch_write_item.delay(SALES, sales)
    batch_write_item.delay(PROFIT, profits)
    batch_write_item.delay(TRAFFIC, traffics)
    batch_write_item.delay(SALES_VOLUMES, sales_volumes)

    return True


def save_week_data(cm_id, store_id, start=None, end=None):
    """

    :param cm_id:
    :param store_id:
    :param start:
    :param end:
    :return:
    """

    if start is None and end is None:
        # 初始化

        start = datetime.datetime(2016, 1, 4)
        today = datetime.datetime.today()
        monday = today - datetime.timedelta(today.weekday())
        end = monday - datetime.timedelta(days=1)
        end = datetime.datetime(end.year, end.month, end.day)
        while start < end:
            sunday = start + datetime.timedelta(days=6)

            start_str = start.strftime('%Y-%m-%d')

            sunday_str = sunday.strftime('%Y-%m-%d')

            price_band_df = Select.select_item_week_price_band(
                cm_id, store_id, start_str, sunday_str)
            sku_df = Select.select_item_week_sku(cm_id, store_id, start_str,
                                                 sunday_str)
            sku_data = transform_cat_sku(cm_id, store_id, sku_df, start_str,
                                         sunday_str)
            batch_write_item.delay(ITEMS, sku_data)
            price_band_data = transform_cat_price_band(
                cm_id, store_id, price_band_df, start_str, sunday_str)
            batch_write_item.delay(ITEMS, price_band_data)
            start = sunday + datetime.timedelta(days=1)
    else:
        price_band_df = Select.select_item_week_price_band(
            cm_id, store_id, start, end)
        sku_df = Select.select_item_week_sku(cm_id, store_id, start, end)
        sku_data = transform_cat_sku(cm_id, store_id, sku_df, start, end)

        batch_write_item.delay(ITEMS, sku_data)
        price_band_data = transform_cat_price_band(cm_id, store_id,
                                                   price_band_df, start, end)

        batch_write_item.delay(ITEMS, price_band_data)

    return True


def save_month_data(cm_id, store_id, start, end):
    """

    :param cm_id:
    :param store_id:
    :param start:
    :param end:
    :return:
    """
    end_date = datetime.datetime.strptime(end, '%Y-%m-%d')
    import calendar
    days = calendar.monthrange(end_date.year, end_date.month)[1]
    if end_date.day < days:
        temp_month = end_date.month - 1
        temp_day = calendar.monthrange(end_date.year, temp_month)[1]
        if temp_month > 9:
            tem_date = str(
                end_date.year) + '-' + str(temp_month) + '-' + str(temp_day)
        else:
            tem_date = str(
                end_date.year) + '-0' + str(temp_month) + '-' + str(temp_day)
        end = tem_date
    data_dict = Select.select_store_month(cm_id, store_id, start, end)
    sales, profits, traffics, order_price, sales_volumes = get_month_items(
        cm_id, store_id, data_dict)

    batch_write_item.delay(SALES, sales)
    batch_write_item.delay(PROFIT, profits)
    batch_write_item.delay(TRAFFIC, traffics)
    batch_write_item.delay(ORDER, traffics)
    batch_write_item.delay(SALES_VOLUMES, sales_volumes)

    # 平均 客单价

    # 品类
    # lv1
    data_dict = Select.select_cat_lv1_month(cm_id, store_id, start, end)
    sales, profits, traffics, sales_volumes = get_month_cat_items(
        cm_id, store_id, data_dict)

    batch_write_item.delay(SALES, sales)
    batch_write_item.delay(PROFIT, profits)
    batch_write_item.delay(TRAFFIC, traffics)
    batch_write_item.delay(SALES_VOLUMES, sales_volumes)

    # lV2
    data_dict = Select.select_cat_lv2_month(cm_id, store_id, start, end)
    sales, profits, traffics, sales_volumes = get_month_cat_items(
        cm_id, store_id, data_dict)

    batch_write_item.delay(SALES, sales)
    batch_write_item.delay(PROFIT, profits)
    batch_write_item.delay(TRAFFIC, traffics)
    batch_write_item.delay(SALES_VOLUMES, sales_volumes)

    # lV3
    data_dict = Select.select_cat_lv3_month(cm_id, store_id, start, end)
    sales, profits, traffics, sales_volumes = get_month_cat_items(
        cm_id, store_id, data_dict)

    batch_write_item.delay(SALES, sales)
    batch_write_item.delay(PROFIT, profits)
    batch_write_item.delay(TRAFFIC, traffics)
    batch_write_item.delay(SALES_VOLUMES, sales_volumes)

    # # lV4
    data_dict = Select.select_cat_lv4_month(cm_id, store_id, start, end)
    sales, profits, traffics, sales_volumes = get_month_cat_items(
        cm_id, store_id, data_dict)

    batch_write_item.delay(SALES, sales)
    batch_write_item.delay(PROFIT, profits)
    batch_write_item.delay(TRAFFIC, traffics)
    batch_write_item.delay(SALES_VOLUMES, sales_volumes)

    return True


def save_year_data(cm_id, store_id, start, end):
    """

    :param cm_id:
    :param store_id:
    :param start:
    :param end:
    :return:
    """
    data_dict = Select.select_store_year(cm_id, store_id, start, end)
    sales, profits, traffics, order_price, sales_volumes = get_year_items(
        cm_id, store_id, data_dict)

    batch_write_item.delay(SALES, sales)
    batch_write_item.delay(PROFIT, profits)
    batch_write_item.delay(TRAFFIC, traffics)
    batch_write_item.delay(ORDER, traffics)
    batch_write_item.delay(SALES_VOLUMES, sales_volumes)

    # LV1
    data_dict = Select.select_cat_lv1_year(cm_id, store_id, start, end)
    sales, profits, traffics, sales_volumes = get_year_cat_items(
        cm_id, store_id, data_dict)

    batch_write_item.delay(SALES, sales)
    batch_write_item.delay(PROFIT, profits)
    batch_write_item.delay(TRAFFIC, traffics)
    batch_write_item.delay(SALES_VOLUMES, sales_volumes)

    # LV2
    data_dict = Select.select_cat_lv2_year(cm_id, store_id, start, end)
    sales, profits, traffics, sales_volumes = get_year_cat_items(
        cm_id, store_id, data_dict)
    batch_write_item.delay(SALES, sales)
    batch_write_item.delay(PROFIT, profits)
    batch_write_item.delay(TRAFFIC, traffics)
    batch_write_item.delay(SALES_VOLUMES, sales_volumes)
    #
    # # LV3
    data_dict = Select.select_cat_lv3_year(cm_id, store_id, start, end)
    sales, profits, traffics, sales_volumes = get_year_cat_items(
        cm_id, store_id, data_dict)
    batch_write_item.delay(SALES, sales)
    batch_write_item.delay(PROFIT, profits)
    batch_write_item.delay(TRAFFIC, traffics)
    batch_write_item.delay(SALES_VOLUMES, sales_volumes)
    #
    # # LV4
    #
    data_dict = Select.select_cat_lv4_year(cm_id, store_id, start, end)
    sales, profits, traffics, sales_volumes = get_year_cat_items(
        cm_id, store_id, data_dict)
    batch_write_item.delay(SALES, sales)
    batch_write_item.delay(PROFIT, profits)
    batch_write_item.delay(TRAFFIC, traffics)
    batch_write_item.delay(SALES_VOLUMES, sales_volumes)

    return True


def get_day_items(cm_id, store_id, data_dict):
    """
    获取销售额， 毛利额， 客流量，平均客单价
    品类销售额， 毛利额， 客流量
    :param cm_id:
    :param store_id:
    :param start:
    :param end:
    :return:
    """

    sales_items = []
    profit_items = []
    traffic_items = []
    order_prices = []
    sales_volumes = []

    for data in data_dict:
        key = 'day' + ':' + str(
            cm_id) + ':' + store_id + ':' + data['date'].strftime('%Y-%m-%d')
        sales_item = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': str(data['sales'])
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }

        sales_items.append(sales_item)

        profit_item = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': str(data['profit'])
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }
        profit_items.append(profit_item)

        traffic_item = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': str(data['traffic'])
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }
        traffic_items.append(traffic_item)

        price_item = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': str(data['avg_price'])
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }
        order_prices.append(price_item)

        sales_volume = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': str(data['sales_volume'])
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }
        sales_volumes.append(sales_volume)

    return (sales_items, profit_items, traffic_items, order_prices,
            sales_volumes)


def get_month_items(cm_id, store_id, data_dict):

    sales_items = []
    profit_items = []
    traffic_items = []
    order_prices = []
    sales_volumes = []

    for data in data_dict:
        last_date = get_month_last(data['month'])
        last_date = last_date.strftime('%Y-%m-%d')
        date = data['month'].strftime('%Y-%m-%d')
        key = 'month' + ':' + str(
            cm_id) + ':' + store_id + ':' + date + ':' + last_date
        sales_item = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': str(data['sales'])
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }

        sales_items.append(sales_item)

        profit_item = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': str(data['profit'])
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }
        profit_items.append(profit_item)

        traffic_item = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': str(data['traffic'])
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }
        traffic_items.append(traffic_item)

        price_item = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': str(data['avg_price'])
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }
        order_prices.append(price_item)

        sales_volume = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': str(data['sales_volume'])
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }
        sales_volumes.append(sales_volume)

    return (sales_items, profit_items, traffic_items, order_prices,
            sales_volumes)


def get_year_items(cm_id, store_id, data_dict):

    sales_items = []
    profit_items = []
    traffic_items = []
    order_prices = []
    sales_volumes = []

    for data in data_dict:
        key = 'year' + ':' + str(cm_id) + ':' + store_id + ':' + str(
            int(data['year'].year))
        sales_item = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': str(data['sales'])
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }

        sales_items.append(sales_item)

        profit_item = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': str(data['profit'])
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }
        profit_items.append(profit_item)

        traffic_item = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': str(data['traffic'])
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }
        traffic_items.append(traffic_item)

        price_item = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': str(data['avg_price'])
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }
        order_prices.append(price_item)

        sales_volume = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': str(data['sales_volume'])
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }
        sales_volumes.append(sales_volume)

    return (sales_items, profit_items, traffic_items, order_prices,
            sales_volumes)


def get_day_cat_items(cm_id, store_id, data_dict):
    """
    品类销售额，毛利额，客流量
    :param data_dict:
    :param cm_id:
    :param store_id:
    :return:
    """

    sales_items = []
    profit_items = []
    traffic_items = []
    sales_volumes = []

    for data in data_dict:
        key = 'day' + ':' + 'cat' + ':' + str(
            cm_id) + ':' + store_id + ':' + str(data['id'].replace(
                ' ', '')) + ':' + data['date'].strftime('%Y-%m-%d')
        sales_item = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': str(data['sales'])
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }

        sales_items.append(sales_item)

        profit_item = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': str(data['profit'])
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }
        profit_items.append(profit_item)

        traffic_item = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': str(data['order_num'])
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }
        traffic_items.append(traffic_item)

        sales_volume = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': str(data['sales_volume'])
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }
        sales_volumes.append(sales_volume)

    return sales_items, profit_items, traffic_items, sales_volumes


def get_month_cat_items(cm_id, store_id, data_dict):

    sales_items = []
    profit_items = []
    traffic_items = []
    sales_volumes = []

    for data in data_dict:
        last_date = get_month_last(data['month'])
        last_date = last_date.strftime('%Y-%m-%d')
        date = data['month'].strftime('%Y-%m-%d')
        key = 'month' + ':' + 'cat' + ':' + str(
            cm_id) + ':' + store_id + ':' + str(data['id'].replace(
                ' ', '')) + ':' + date + ':' + last_date
        sales_item = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': str(data['sales'])
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }

        sales_items.append(sales_item)

        profit_item = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': str(data['profit'])
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }
        profit_items.append(profit_item)

        traffic_item = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': str(data['order_num'])
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }
        traffic_items.append(traffic_item)

        sales_volume = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': str(data['sales_volume'])
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }
        sales_volumes.append(sales_volume)

    return sales_items, profit_items, traffic_items, sales_volumes


def get_year_cat_items(cm_id, store_id, data_dict):

    sales_items = []
    profit_items = []
    traffic_items = []
    sales_volumes = []

    for data in data_dict:
        key = 'year' + ':' + 'cat' + ':' + str(
            cm_id) + ':' + store_id + ':' + str(data['id'].replace(
                ' ', '')) + ':' + str(int(data['year']))
        sales_item = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': str(data['sales'])
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }

        sales_items.append(sales_item)

        profit_item = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': str(data['profit'])
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }
        profit_items.append(profit_item)

        traffic_item = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': str(data['order_num'])
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }
        traffic_items.append(traffic_item)

        sales_volume = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': str(data['sales_volume'])
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }
        sales_volumes.append(sales_volume)

    return sales_items, profit_items, traffic_items, sales_volumes


def transform_cat_sku(cm_id, store_id, data, start, end):
    sku_dict = {}
    # key = '{}:{}:'.format(cm_id, store_id)
    for sku_item in data:
        _key = ''
        if sku_item['cat_lv1_id']:
            if sku_item['cat_lv1_id'].strip() != '':
                _key = _key + sku_item['cat_lv1_id'].strip()
        if sku_item['cat_lv2_id']:
            if sku_item['cat_lv2_id'].strip() != '':
                _key = _key + ':' + sku_item['cat_lv2_id'].strip()
        if sku_item['cat_lv3_id']:
            if sku_item['cat_lv3_id'].strip() != '':
                _key = _key + ':' + sku_item['cat_lv3_id'].strip()
        if sku_item['cat_lv4_id']:
            if sku_item['cat_lv4_id'].strip() != '':
                _key = _key + ':' + sku_item['cat_lv4_id'].strip()

        if _key not in sku_dict:
            sku_dict[_key] = {'price': [], 'sku_num': []}
        sku_dict[_key]['price'].append(sku_item['price'])
        sku_dict[_key]['sku_num'].append(sku_item['sku_num'])
    data_list = []
    periods = start + ':' + end
    for k, v in sku_dict.items():

        key = str(cm_id) + ':' + str(store_id) + ':sku:' + k + ':' + periods
        sku_item = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': json.dumps(v)
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }
        data_list.append(sku_item)

    return data_list


def transform_cat_price_band(cm_id, store_id, data, start, end):
    periods = start + ':' + end
    price_dict = {}
    for item in data:
        _key = ''
        if item['cat_lv1_id']:
            if item['cat_lv1_id'].strip() != '':
                _key = _key + item['cat_lv1_id'].strip()
        if item['cat_lv2_id'] and item['cat_lv2_id'] != '':
            if item['cat_lv2_id'].strip() != '':
                _key = _key + ':' + item['cat_lv2_id'].strip()
        if item['cat_lv3_id'] and item['cat_lv3_id'] != '':
            if item['cat_lv3_id'].strip() != '':
                _key = _key + ':' + item['cat_lv3_id'].strip()
        if item['cat_lv4_id'] and item['cat_lv4_id'] != '':
            if item['cat_lv4_id'].strip() != '':
                _key = _key + ':' + item['cat_lv4_id'].strip()

        if _key not in price_dict:
            price_dict[_key] = {
                'price': [],
                'profit': [],
                'sales_volume': [],
                'item_name': [],
                'item_id': [],
            }
        price_dict[_key]['price'].append(item['price'])
        price_dict[_key]['profit'].append(item['profit'])
        price_dict[_key]['sales_volume'].append(item['sales_volume'])
        price_dict[_key]['item_name'].append(item['item_name'].strip())
        price_dict[_key]['item_id'].append(item['item_id'].replace(' ', ''))
    data_list = []
    for k, v in price_dict.items():
        key = str(cm_id) + ':' + str(
            store_id) + ':price_band:' + k + ':' + periods
        price_item = {
            'PutRequest': {
                'Item': {
                    'key': {
                        'S': key
                    },
                    'value': {
                        'S': json.dumps(v)
                    },
                    'chain_store_id': {
                        'S': str(cm_id)
                    }
                }
            }
        }
        data_list.append(price_item)

    return data_list


@celery_app.task
def batch_write_item(table_name, items):
    """
        批量插入item
        """
    import boto3
    client = boto3.client('dynamodb')
    while len(items) > 0:
        item_list = items[0:20]
        request_items = {table_name: item_list}
        response = client.batch_write_item(RequestItems=request_items)
        items = items[20:]
        if response['UnprocessedItems']:
            print('1 -- {}'.format(len(items)))
            items = items + response['UnprocessedItems'][table_name]
            print('2 -- {}'.format(len(items)))
        print(len(items))

    return True
