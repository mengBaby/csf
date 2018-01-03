from sqlalchemy import text
import pandas
import datetime
import logging
from utils.engine_config import RS_ENGINE
from utils.time_utils import get_last_year_date, \
    get_today_str
from tasks.sql_operation.sql_utils import is_exist_in_summary, \
    delete_data


def save_cat_summary(chain_store_id,
                     store_id,
                     record_date):
    # 品类1

    delete_data(chain_store_id,
                store_id,
                record_date,
                record_date,
                "ddrs_cat_lv1_summary")

    save_cat_summary_single(chain_store_id,
                            store_id,
                            record_date,
                            'ddrs_cat_lv1_summary',
                            'foreign_category_lv1',
                            'foreign_category_lv1_name')
    # 品类2

    delete_data(chain_store_id,
                store_id,
                record_date,
                record_date,
                "ddrs_cat_lv2_summary")

    save_cat_summary_single(chain_store_id,
                            store_id,
                            record_date,
                            'ddrs_cat_lv2_summary',
                            'foreign_category_lv2',
                            'foreign_category_lv2_name')

    delete_data(chain_store_id,
                store_id,
                record_date,
                record_date,
                "ddrs_cat_lv3_summary")

    save_cat_summary_single(chain_store_id,
                            store_id,
                            record_date,
                            'ddrs_cat_lv3_summary',
                            'foreign_category_lv3',
                            'foreign_category_lv3_name')

    delete_data(chain_store_id,
                store_id,
                record_date,
                record_date,
                "ddrs_cat_lv4_summary")

    save_cat_summary_single(chain_store_id,
                            store_id,
                            record_date,
                            'ddrs_cat_lv4_summary',
                            'foreign_category_lv4',
                            'foreign_category_lv4_name')

    return True


def save_cat_summary_init(chain_store_id,
                          store_id):
    """
    初始化
    :param chain_store_id:
    :param store_id:
    :return: True
    """
    start = '2016-01-01'
    end = get_today_str(days=-1)

    save_cat_summary_multiple(chain_store_id,
                              store_id,
                              'ddrs_cat_lv1_summary',
                              'foreign_category_lv1',
                              'foreign_category_lv1_name',
                              start,
                              end)
    save_cat_summary_multiple(chain_store_id,
                              store_id,
                              'ddrs_cat_lv2_summary',
                              'foreign_category_lv2',
                              'foreign_category_lv2_name',
                              start,
                              end)
    save_cat_summary_multiple(chain_store_id,
                              store_id,
                              'ddrs_cat_lv3_summary',
                              'foreign_category_lv3',
                              'foreign_category_lv3_name',
                              start,
                              end)

    return True


def save_cat_summary_manual(chain_store_id,
                            store_id,
                            start=None,
                            end=None):
    """
    手动调用的时候用
    :param chain_store_id:
    :param store_id:
    :param start:
    :param end:
    :return:
    """
    delete_data(chain_store_id,
                store_id,
                start,
                end,
                "ddrs_cat_lv1_summary")

    delete_data(chain_store_id,
                store_id,
                start,
                end,
                "ddrs_cat_lv2_summary")

    delete_data(chain_store_id,
                store_id,
                start,
                end,
                "ddrs_cat_lv3_summary")

    delete_data(chain_store_id,
                store_id,
                start,
                end,
                "ddrs_cat_lv4_summary")

    save_cat_summary_multiple(chain_store_id,
                              store_id,
                              'ddrs_cat_lv1_summary',
                              'foreign_category_lv1',
                              'foreign_category_lv1_name',
                              start,
                              end)
    save_cat_summary_multiple(chain_store_id,
                              store_id,
                              'ddrs_cat_lv2_summary',
                              'foreign_category_lv2',
                              'foreign_category_lv2_name',
                              start,
                              end)
    save_cat_summary_multiple(chain_store_id,
                              store_id,
                              'ddrs_cat_lv3_summary',
                              'foreign_category_lv3',
                              'foreign_category_lv3_name',
                              start,
                              end)

    save_cat_summary_multiple(chain_store_id,
                              store_id,
                              'ddrs_cat_lv4_summary',
                              'foreign_category_lv4',
                              'foreign_category_lv4_name',
                              start,
                              end)

    return True


def save_cat_summary_multiple(chain_store_id,
                              store_id,
                              table_name,
                              cat_lv,
                              cat_lv_name,
                              start,
                              end):
    """

    :param table_name:
    :param end:
    :param start:
    :param chain_store_id:
    :param store_id:
    :param cat_lv:
    :param cat_lv_name:
    :return: True
    """
    insert_query = """
        INSERT INTO {}
        (
            SELECT
                recorddate AS date,
                EXTRACT(hour FROM saletime) AS hour,
                {} AS id,
                {} AS name,
                SUM(subtotal::NUMERIC(10,2)) AS sales,
                (SUM(subtotal::NUMERIC(10,2)) -
                SUM(quantity::NUMERIC(10,2) *
                lastinprice::NUMERIC(10,2)))::NUMERIC(10,2) AS profit,
                cmid,
                foreign_store_id,
                getdate() AS last_updated,
                COUNT(DISTINCT receipt_id) AS order_num,
                SUM(quantity::NUMERIC(10,2)) AS sales_volume
            FROM
                goodsflow
            WHERE
                recorddate >='{}'
            AND
                recorddate <='{}'
            AND
                cmid = {}
            AND
                foreign_store_id = '{}'
            GROUP BY
                date,
                hour,
                id,
                name,
                cmid,
                foreign_store_id
        )
    """.format(table_name,
               cat_lv,
               cat_lv_name,
               start,
               end,
               chain_store_id,
               store_id)
    RS_ENGINE.execute(
        text(insert_query).execution_options(autocommit=True)
    )

    return True


def save_cat_summary_single(chain_store_id,
                            store_id,
                            record_date,
                            table_name,
                            cat_lv,
                            cat_lv_name):
    """
    每天调用
    :param table_name:
    :param chain_store_id:
    :param store_id:
    :param record_date:
    :param cat_lv:
    :param cat_lv_name:
    :return:
    """
    insert_query = """
        INSERT INTO {}
        (
            SELECT
                recorddate AS date,
                EXTRACT(hour FROM saletime) AS hour,
                {} AS id,
                {} AS name,
                SUM(subtotal::NUMERIC(10,2)) AS sales,
                (SUM(subtotal::NUMERIC(10,2)) -
                SUM(quantity::NUMERIC(10,2) *
                lastinprice::NUMERIC(10,2)))::NUMERIC(10,2) AS profit,
                cmid,
                foreign_store_id,
                getdate() AS last_updated,
                COUNT(DISTINCT receipt_id) AS order_num,
                SUM(quantity::NUMERIC(10,2)) AS sales_volume
            FROM
                goodsflow
            WHERE
                recorddate ='{}'
            AND
                cmid = {}
            AND
                foreign_store_id = '{}'
            GROUP BY
                date,
                hour,
                id,
                name,
                cmid,
                foreign_store_id
        )
    """.format(table_name,
               cat_lv,
               cat_lv_name,
               record_date,
               chain_store_id,
               store_id)
    RS_ENGINE.execute(
        text(insert_query).execution_options(autocommit=True)
    )
    return True
