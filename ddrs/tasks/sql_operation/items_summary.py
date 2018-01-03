from sqlalchemy import text
import pandas
import datetime
import logging
from utils.engine_config import RS_ENGINE
from utils.time_utils import get_last_year_date, \
    get_today_str
from tasks.sql_operation.sql_utils import is_exist_in_summary, \
    delete_data


def save_item_summary_init(chain_store_id, store_id):
    end = get_today_str(days=-1)
    insert_query = """
        INSERT INTO ddrs_item_summary
        (
            SELECT
                recorddate AS date,
                getdate() AS last_updated,
                cmid,
                foreign_store_id,
                foreign_category_lv1 AS cat_lv1_id,
                foreign_category_lv1_name AS cat_lv1_name,
                foreign_category_lv2 AS cat_lv2_id,
                foreign_category_lv2_name AS cat_lv2_name,
                foreign_category_lv3 AS cat_lv3_id,
                foreign_category_lv3_name AS cat_lv3_name,
                foreign_category_lv4 AS cat_lv4_id,
                foreign_category_lv4_name AS cat_lv4_name,
                item_name AS item_name,
                SUM(subtotal::NUMERIC(10,2)) AS sales,
                SUM(quantity::NUMERIC(10,2)) AS sales_volume,
                (SUM(subtotal::NUMERIC(10,2)) -
                SUM(quantity::NUMERIC(10,2) *
                lastinprice::NUMERIC(10,2))) AS profit,
                MIN(saleprice) AS price,
                EXTRACT(hour from saletime) AS hour,
                foreign_item_id AS item_id
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
                hour,
                cat_lv1_id,
                cat_lv1_name,
                cat_lv2_id,
                cat_lv2_name,
                cat_lv3_id,
                cat_lv3_name,
                cat_lv4_id,
                cat_lv4_name,
                item_id,
                item_name
        )
    """.format(end, chain_store_id, store_id)
    RS_ENGINE.execute(text(insert_query).execution_options(autocommit=True), )

    return True


def save_item_summary_manual(chain_store_id, store_id, start=None, end=None):

    delete_data(chain_store_id, store_id, start, end, 'ddrs_item_summary')

    insert_query = """
        INSERT INTO ddrs_item_summary
        (
            SELECT
                recorddate AS date,
                getdate() AS last_updated,
                cmid,
                foreign_store_id,
                foreign_category_lv1 AS cat_lv1_id,
                foreign_category_lv1_name AS cat_lv1_name,
                foreign_category_lv2 AS cat_lv2_id,
                foreign_category_lv2_name AS cat_lv2_name,
                foreign_category_lv3 AS cat_lv3_id,
                foreign_category_lv3_name AS cat_lv3_name,
                foreign_category_lv4 AS cat_lv4_id,
                foreign_category_lv4_name AS cat_lv4_name,
                item_name AS item_name,
                SUM(subtotal::NUMERIC(10,2)) AS sales,
                SUM(quantity::NUMERIC(10,2)) AS sales_volume,
                (SUM(subtotal::NUMERIC(10,2)) -
                SUM(quantity::NUMERIC(10,2) *
                lastinprice::NUMERIC(10,2))) AS profit,
                MIN(saleprice) AS price,
                EXTRACT(hour from saletime) AS hour,
                foreign_item_id AS item_id
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
                hour,
                cat_lv1_id,
                cat_lv1_name,
                cat_lv2_id,
                cat_lv2_name,
                cat_lv3_id,
                cat_lv3_name,
                cat_lv4_id,
                cat_lv4_name,
                item_id,
                item_name
        )
    """.format(start, end, chain_store_id, store_id)
    RS_ENGINE.execute(text(insert_query).execution_options(autocommit=True), )

    return True


def save_item_summary(chain_store_id, store_id, record_date):
    """
    每天调用
    :param chain_store_id:
    :param store_id:
    :param record_date:
    :return:
    """

    delete_data(chain_store_id, store_id, record_date, record_date,
                'ddrs_item_summary')

    insert_query = """
        INSERT INTO ddrs_item_summary
        (
            SELECT
                recorddate AS date,
                getdate() AS last_updated,
                cmid,
                foreign_store_id,
                foreign_category_lv1 AS cat_lv1_id,
                foreign_category_lv1_name AS cat_lv1_name,
                foreign_category_lv2 AS cat_lv2_id,
                foreign_category_lv2_name AS cat_lv2_name,
                foreign_category_lv3 AS cat_lv3_id,
                foreign_category_lv3_name AS cat_lv3_name,
                foreign_category_lv4 AS cat_lv4_id,
                foreign_category_lv4_name AS cat_lv4_name,
                item_name AS item_name,
                SUM(subtotal::NUMERIC(10,2)) AS sales,
                SUM(quantity::NUMERIC(10,2)) AS sales_volume,
                (SUM(subtotal::NUMERIC(10,2)) -
                SUM(quantity::NUMERIC(10,2) *
                lastinprice::NUMERIC(10,2))) AS profit,
                MIN(saleprice) AS price,
                EXTRACT(hour from saletime) AS hour,
                foreign_item_id AS item_id
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
                hour,
                cat_lv1_id,
                cat_lv1_name,
                cat_lv2_id,
                cat_lv2_name,
                cat_lv3_id,
                cat_lv3_name,
                cat_lv4_id,
                cat_lv4_name,
                item_id,
                item_name
        )
    """.format(record_date, chain_store_id, store_id)
    RS_ENGINE.execute(text(insert_query).execution_options(autocommit=True), )

    return True
