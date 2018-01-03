from sqlalchemy import text
import pandas
import datetime
import logging
from utils.engine_config import RS_ENGINE
from utils.time_utils import get_last_year_date, \
    get_today_str
from tasks.sql_operation.sql_utils import is_exist_in_summary, \
    delete_data


def save_store_summary_init(chain_store_id,
                            store_id):
    """
    初始化调用
    :param chain_store_id:
    :param store_id:
    :param end:
    :return:
    """
    end = get_today_str(days=-1)
    insert_query = """
        INSERT INTO ddrs_store_summary
        (
            SELECT
                EXTRACT(hour from saletime) AS hour,
                recorddate AS date,
                SUM(subtotal::NUMERIC(10,2)) AS sales,
                (SUM(subtotal::NUMERIC(10,2)) -
                SUM(quantity::NUMERIC(10,2) *
                lastinprice::NUMERIC(10,2))) AS profit,
                COUNT(DISTINCT receipt_id) AS traffic,
                cmid,
                foreign_store_id,
                getdate() AS last_updated,
                SUM(quantity::NUMERIC(10,2)) AS sales_volume
            FROM
                goodsflow
            WHERE
                recorddate >= '2016-01-01'
            AND
                recorddate <= '{}'
            AND
                cmid = {}
            AND
                foreign_store_id = '{}'
            GROUP BY
                date,
                cmid,
                foreign_store_id,
                hour
        )
    """.format(end,
               chain_store_id,
               store_id)
    RS_ENGINE.execute(
        text(insert_query).execution_options(autocommit=True),
    )

    return True


def save_store_summary_manual(chain_store_id,
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
                'ddrs_store_summary')
    insert_query = """
        INSERT INTO ddrs_store_summary
        (
            SELECT
                EXTRACT(hour from saletime) AS hour,
                recorddate AS date,
                SUM(subtotal::NUMERIC(10,2)) AS sales,
                (SUM(subtotal::NUMERIC(10,2)) -
                SUM(quantity::NUMERIC(10,2) *
                lastinprice::NUMERIC(10,2))) AS profit,
                COUNT(DISTINCT receipt_id) AS traffic,
                cmid,
                foreign_store_id,
                getdate() AS last_updated,
                SUM(quantity::NUMERIC(10,2)) AS sales_volume
            FROM
                goodsflow
            WHERE
                recorddate >= '{}'
            AND
                recorddate <= '{}'
            AND
                cmid = {}
            AND
                foreign_store_id = '{}'
            GROUP BY
                date,
                cmid,
                foreign_store_id,
                hour
        )
    """.format(start,
               end,
               chain_store_id,
               store_id)
    RS_ENGINE.execute(
        text(insert_query).execution_options(autocommit=True),
    )
    return True


def save_store_summary(chain_store_id,
                       store_id,
                       record_date):
    """
    每天调用
    :param chain_store_id:
    :param store_id:
    :param record_date:
    :return:
    """

    delete_data(chain_store_id,
                store_id,
                record_date,
                record_date,
                'ddrs_store_summary')
    insert_query = """
        insert into ddrs_store_summary
        (
            SELECT
                EXTRACT(hour from saletime) AS hour,
                recorddate AS date,
                SUM(subtotal::NUMERIC(10,2)) AS sales,
                (SUM(subtotal::NUMERIC(10,2)) -
                SUM(quantity::NUMERIC(10,2) *
                lastinprice::NUMERIC(10,2))) AS profit,
                COUNT(DISTINCT receipt_id) AS traffic,
                cmid,
                foreign_store_id,
                getdate() AS last_updated,
                SUM(quantity::NUMERIC(10,2)) AS sales_volume
            FROM
                goodsflow
            WHERE
                recorddate = '{}'
            AND
                cmid = {}
            AND
                foreign_store_id = '{}'
            GROUP BY
                date,
                cmid,
                foreign_store_id,
                hour
        )
    """.format(record_date,
               chain_store_id,
               store_id)
    RS_ENGINE.execute(
        text(insert_query).execution_options(autocommit=True),
    )
    return True
