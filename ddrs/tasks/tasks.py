import datetime
import requests
import logging
from tasks import celery_app
from models.model import Record
from tasks.sql_operation.store_summary import save_store_summary_init, \
    save_store_summary, save_store_summary_manual
from tasks.sql_operation.category_summary import save_cat_summary, \
    save_cat_summary_init, save_cat_summary_manual
from tasks.sql_operation.order_summary import save_order_summary, \
    save_order_summary_init, save_order_summary_manual
from tasks.sql_operation.items_summary import save_item_summary, \
    save_item_summary_init, save_item_summary_manual
from tasks.sql_operation.dynamodb import get_day_items, \
    save_day_data, save_month_data, save_year_data, save_week_data
from utils.time_utils import get_today_str


@celery_app.task
def gen_everyday_summary(chain_store_id, store_id, start=None, end=None):
    """
    # 生成每天的summary
    :param chain_store_id:
    :param store_id:
    :param start:
    :param end:
    :return:
    """
    if start and end is None:
        save_store_summary(chain_store_id, store_id, start)

        save_order_summary(chain_store_id, store_id, start)

        save_cat_summary(chain_store_id, store_id, start)

        save_item_summary(chain_store_id, store_id, start)

        record = Record(
            cm_id=chain_store_id,
            foreign_store_id=store_id,
            date=start,
            last_update=datetime.datetime.now(),
        )
        record.save()
        return True

    if start and end:
        save_store_summary_manual(chain_store_id, store_id, start, end)

        save_cat_summary_manual(chain_store_id, store_id, start, end)

        save_order_summary_manual(chain_store_id, store_id, start, end)

        save_item_summary_manual(chain_store_id, store_id, start, end)

        record = Record(
            cm_id=chain_store_id,
            foreign_store_id=store_id,
            date=start,
            last_update=datetime.datetime.now(),
        )
        record.save()
        return True

    if start is None and end is not None:
        return False
    save_store_summary_init(chain_store_id, store_id)
    save_order_summary_init(chain_store_id, store_id)
    save_cat_summary_init(chain_store_id, store_id)
    save_item_summary_init(chain_store_id, store_id)
    record = Record(
        cm_id=chain_store_id,
        foreign_store_id=store_id,
        date=datetime.datetime.now(),
        last_update=datetime.datetime.now(),
    )
    record.save()
    return True


@celery_app.task
def gen_everyday_item_summary(chain_store_id, store_id, start=None, end=None):
    """
    生成每天的item summary
    :param chain_store_id:
    :param store_id:
    :param start:
    :param end:
    :return:
    """
    if start and end is None:
        save_item_summary(chain_store_id, store_id, start)
        record = Record(
            cm_id=chain_store_id,
            foreign_store_id=store_id,
            date=start,
            last_update=datetime.datetime.now(),
        )
        record.save()
        return True

    if start and end:
        save_item_summary_manual(chain_store_id, store_id, start, end)

        record = Record(
            cm_id=chain_store_id,
            foreign_store_id=store_id,
            date=start,
            last_update=datetime.datetime.now(),
        )
        record.save()
        return True

    if start is None and end is not None:
        return False
    save_item_summary_init(chain_store_id, store_id)
    record = Record(
        cm_id=chain_store_id,
        foreign_store_id=store_id,
        date=datetime.datetime.now(),
        last_update=datetime.datetime.now(),
    )
    record.save()
    return True


@celery_app.task
def gen_dynamodb_data(flag, chain_store_id, store_id, start=None, end=None):
    """
    生成初始化的数据
    :param flag:
    :param chain_store_id:
    :param store_id:
    :param start:
    :param end:
    :return:
    """
    if flag:
        save_day_data(chain_store_id, store_id, start, end)
        save_week_data(chain_store_id, store_id)
        save_month_data(chain_store_id, store_id, start, end)
        return 'init 保存到DynamoDB 成功!'
    return 'flag is False'


@celery_app.task
def gen_dynamodb_month_data(flag,
                            chain_store_id,
                            store_id,
                            start=None,
                            end=None):
    """
    生成初始化的数据
    :param flag:
    :param chain_store_id:
    :param store_id:
    :param start:
    :param end:
    :return:
    """
    if flag:
        save_month_data(chain_store_id, store_id, start, end)
        return 'init 保存到DynamoDB 成功!'
    return 'flag is False'


@celery_app.task
def gen_dynamodb_day_data(flag, chain_store_id, store_id, start=None,
                          end=None):
    """
    生成每天的dynamodb数据
    :param flag:
    :param chain_store_id:
    :param store_id:
    :param start:
    :param end:
    :return:
    """
    today = get_today_str(days=-1)
    if flag:
        save_day_data(chain_store_id, store_id, start, end)
        return '{}--保存到DynamoDB 成功!'.format(today)
    return 'flag is False'


@celery_app.task
def gen_dynamodb_week_data(flag,
                           chain_store_id,
                           store_id,
                           start=None,
                           end=None):
    """
    生成每周的dynamoDB数据
    :param flag:
    :param chain_store_id:
    :param store_id:
    :param start:
    :param end:
    :return:
    """
    today = get_today_str(days=-1)
    if flag and start is None and end is None:
        save_week_data(chain_store_id, store_id)
        return '{}--周数据保存DynamoDB 成功!'.format(today)
    if flag and start and end:
        save_week_data(chain_store_id, store_id, start, end)
        return '{}--周数据保存DynamoDB 成功!'.format(today)
    return 'flag is False'


@celery_app.task
def gen_test(msg):
    if msg:
        return True
    return False
