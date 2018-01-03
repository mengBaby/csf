import pandas
from utils.engine_config import RS_ENGINE
from models.model import Category


class Select:
    def __init__(self):
        pass

    @staticmethod
    def select_store_day(cm_id, store_id, start, end):
        """
        按天取
        :param cm_id:
        :param store_id:
        :param start:
        :param end:
        :return:
        """
        query = """
            SELECT
                date,
                SUM(profit::NUMERIC(10,2)) AS profit,
                SUM(sales::NUMERIC(10,2)) AS sales,
                SUM(traffic) AS traffic,
                (
                SUM(sales::NUMERIC(10,2))/SUM(traffic)
                )::NUMERIC(10,2) as avg_price,
                SUM(sales_volume::NUMERIC(10,2)) AS sales_volume
            FROM
                ddrs_store_summary
            WHERE
                cmid ={}
            AND
                foreign_store_id = '{}'
            AND
                date >= '{}'
            AND
                date <= '{}'
            GROUP BY
                date
        """.format(cm_id, store_id, start, end)
        df = pandas.read_sql(query, RS_ENGINE)
        _dict = df.to_dict("records")
        return _dict

    @staticmethod
    def select_store_month(cm_id, store_id, start, end):
        select_query = """
            SELECT
                to_date(date, 'YYYY-MM-01') as month,
                SUM(profit::NUMERIC(10,2)) AS profit,
                SUM(sales::NUMERIC(10,2)) AS sales,
                SUM(traffic) AS traffic,
                (
                SUM(sales::NUMERIC(10,2))/SUM(traffic)
                )::NUMERIC(10,2) as avg_price,
                SUM(sales_volume::NUMERIC(10,2)) AS sales_volume
            FROM
                ddrs_store_summary
            WHERE
                cmid ={}
            AND
                foreign_store_id = '{}'
            AND
                date >= '{}'
            AND
                date <= '{}'
            GROUP BY
                month
        """.format(cm_id, store_id, start, end)
        df = pandas.read_sql(select_query, RS_ENGINE)
        _dict = df.to_dict("records")
        return _dict

    @staticmethod
    def select_store_quarter(cm_id, store_id, start, end):
        select_query = """
            SELECT
                EXTRACT(QUARTER from date) AS quarter,
                EXTRACT(year from date) AS year,
                SUM(profit::NUMERIC(10,2)) AS profit,
                SUM(sales::NUMERIC(10,2)) AS sales,
                SUM(traffic) AS traffic,
                (
                SUM(sales::NUMERIC(10,2))/SUM(traffic)
                )::NUMERIC(10,2) as avg_price,
                SUM(sales_volume::NUMERIC(10,2)) AS sales_volume
            FROM
                ddrs_store_summary
            WHERE
                cmid = {}
            AND
                foreign_store_id = '{}'
            AND
                date >= '{}'
            AND
                date <= '{}'
            GROUP BY
                year,
                quarter
        """.format(cm_id, store_id, start, end)
        df = pandas.read_sql(select_query, RS_ENGINE)
        _dict = df.to_dict("records")
        return _dict

    @staticmethod
    def select_store_year(cm_id, store_id, start, end):
        select_query = """
            SELECT
                to_date(date, 'YYYY-01-01') AS year,
                SUM(profit::NUMERIC(10,2)) AS profit,
                SUM(sales::NUMERIC(10,2)) AS sales,
                SUM(traffic) AS traffic,
                (
                SUM(sales::NUMERIC(10,2))/SUM(traffic)
                )::NUMERIC(10,2) as avg_price,
                SUM(sales_volume::NUMERIC(10,2)) AS sales_volume
            FROM
                ddrs_store_summary
            WHERE
                cmid = {}
            AND
                foreign_store_id = '{}'
            AND
                date >= '{}'
            AND
                date <= '{}'
            GROUP BY
                year
        """.format(cm_id, store_id, start, end)
        df = pandas.read_sql(select_query, RS_ENGINE)
        _dict = df.to_dict("records")
        return _dict

    @staticmethod
    def select_cat_lv1_day(cm_id, store_id, start, end):
        """
        按品类分销售额，单词，利润
        :param cm_id:
        :param store_id:
        :param start:
        :param end:
        :return:
        """
        select_query = """
            SELECT
                date,
                id,
                SUM(sales::NUMERIC(10,2)) AS sales,
                SUM(profit::NUMERIC(10,2)) AS profit,
                SUM(order_num::NUMERIC(10,2)) AS order_num,
                SUM(sales_volume::NUMERIC(10,2)) AS sales_volume
            FROM
                ddrs_cat_lv1_summary
            WHERE
                cmid ={}
            AND
                foreign_store_id = '{}'
            AND
                date >= '{}'
            AND
                date <= '{}'
            AND
                id  != ''
            GROUP BY
                date,
                id
        """.format(cm_id, store_id, start, end)
        df = pandas.read_sql(select_query, RS_ENGINE)
        _dict = df.to_dict("records")
        return _dict

    @staticmethod
    def select_cat_lv1_month(cm_id, store_id, start, end):
        select_query = """
            SELECT
                to_date(date, 'YYYY-MM-01') as month,
                id,
                SUM(sales::NUMERIC(10,2)) AS sales,
                SUM(profit::NUMERIC(10,2)) AS profit,
                SUM(order_num::NUMERIC(10,2)) AS order_num,
                SUM(sales_volume::NUMERIC(10,2)) AS sales_volume
            FROM
                ddrs_cat_lv1_summary
            WHERE
                cmid ={}
            AND
                foreign_store_id = '{}'
            AND
                date >= '{}'
            AND
                date <= '{}'
            AND
                id  != ''
            GROUP BY
                month,
                id
        """.format(cm_id, store_id, start, end)
        df = pandas.read_sql(select_query, RS_ENGINE)
        _dict = df.to_dict("records")
        return _dict

    @staticmethod
    def select_cat_lv1_year(cm_id, store_id, start, end):
        select_query = """
            SELECT
                EXTRACT(year from date) AS year,
                id,
                SUM(sales::NUMERIC(10,2)) AS sales,
                SUM(profit::NUMERIC(10,2)) AS profit,
                SUM(order_num::NUMERIC(10,2)) AS order_num,
                SUM(sales_volume::NUMERIC(10,2)) AS sales_volume
            FROM
                ddrs_cat_lv1_summary
            WHERE
                cmid ={}
            AND
                foreign_store_id = '{}'
            AND
                date >= '{}'
            AND
                date <= '{}'
            AND
                id  != ''
            GROUP BY
                year,
                id
        """.format(cm_id, store_id, start, end)
        df = pandas.read_sql(select_query, RS_ENGINE)
        _dict = df.to_dict("records")
        return _dict

    @staticmethod
    def select_cat_lv2_day(cm_id, store_id, start, end):
        select_query = """
                SELECT
                    date,
                    id,
                    SUM(sales::NUMERIC(10,2)) AS sales,
                    SUM(profit::NUMERIC(10,2)) AS profit,
                    SUM(order_num::NUMERIC(10,2)) AS order_num,
                    SUM(sales_volume::NUMERIC(10,2)) AS sales_volume
                FROM
                    ddrs_cat_lv2_summary
                WHERE
                    cmid ={}
                AND
                    foreign_store_id = '{}'
                AND
                    date >= '{}'
                AND
                    date <= '{}'
                AND
                    id  != ''
                GROUP BY
                    date,
                    id
            """.format(cm_id, store_id, start, end)
        df = pandas.read_sql(select_query, RS_ENGINE)
        _dict = df.to_dict("records")
        return _dict

    @staticmethod
    def select_cat_lv2_month(cm_id, store_id, start, end):
        select_query = """
                SELECT
                    to_date(date, 'YYYY-MM-01') as month,
                    id,
                    SUM(sales::NUMERIC(10,2)) AS sales,
                    SUM(profit::NUMERIC(10,2)) AS profit,
                    SUM(order_num::NUMERIC(10,2)) AS order_num,
                    SUM(sales_volume::NUMERIC(10,2)) AS sales_volume
                FROM
                    ddrs_cat_lv2_summary
                WHERE
                    cmid ={}
                AND
                    foreign_store_id = '{}'
                AND
                    date >= '{}'
                AND
                    date <= '{}'
                AND
                    id  != ''
                GROUP BY
                    month,
                    id
            """.format(cm_id, store_id, start, end)
        df = pandas.read_sql(select_query, RS_ENGINE)
        _dict = df.to_dict("records")
        return _dict

    @staticmethod
    def select_cat_lv2_year(cm_id, store_id, start, end):
        select_query = """
                SELECT
                    EXTRACT(year from date) AS year,
                    id,
                    SUM(sales::NUMERIC(10,2)) AS sales,
                    SUM(profit::NUMERIC(10,2)) AS profit,
                    SUM(order_num::NUMERIC(10,2)) AS order_num,
                    SUM(sales_volume::NUMERIC(10,2)) AS sales_volume
                FROM
                    ddrs_cat_lv2_summary
                WHERE
                    cmid ={}
                AND
                    foreign_store_id = '{}'
                AND
                    date >= '{}'
                AND
                    date <= '{}'
                AND
                    id  != ''
                GROUP BY
                    year,
                    id
            """.format(cm_id, store_id, start, end)
        df = pandas.read_sql(select_query, RS_ENGINE)
        _dict = df.to_dict("records")
        return _dict

    @staticmethod
    def select_cat_lv3_day(cm_id, store_id, start, end):
        select_query = """
                SELECT
                    date,
                    id,
                    SUM(sales::NUMERIC(10,2)) AS sales,
                    SUM(profit::NUMERIC(10,2)) AS profit,
                    SUM(order_num::NUMERIC(10,2)) AS order_num,
                    SUM(sales_volume::NUMERIC(10,2)) AS sales_volume
                FROM
                    ddrs_cat_lv3_summary
                WHERE
                    cmid ={}
                AND
                    foreign_store_id = '{}'
                AND
                    date >= '{}'
                AND
                    date <= '{}'
                AND
                    id  != ''
                GROUP BY
                    date,
                    id
            """.format(cm_id, store_id, start, end)
        df = pandas.read_sql(select_query, RS_ENGINE)
        _dict = df.to_dict("records")
        return _dict

    @staticmethod
    def select_cat_lv3_month(cm_id, store_id, start, end):
        select_query = """
                SELECT
                    to_date(date, 'YYYY-MM-01') as month,
                    id,
                    SUM(sales::NUMERIC(10,2)) AS sales,
                    SUM(profit::NUMERIC(10,2)) AS profit,
                    SUM(order_num::NUMERIC(10,2)) AS order_num,
                    SUM(sales_volume::NUMERIC(10,2)) AS sales_volume
                FROM
                    ddrs_cat_lv3_summary
                WHERE
                    cmid ={}
                AND
                    foreign_store_id = '{}'
                AND
                    date >= '{}'
                AND
                    date <= '{}'
                AND
                    id  != ''
                GROUP BY
                    month,
                    id
            """.format(cm_id, store_id, start, end)
        df = pandas.read_sql(select_query, RS_ENGINE)
        _dict = df.to_dict("records")
        return _dict

    @staticmethod
    def select_cat_lv3_year(cm_id, store_id, start, end):
        select_query = """
                SELECT
                    EXTRACT(year from date) AS year,
                    id,
                    SUM(sales::NUMERIC(10,2)) AS sales,
                    SUM(profit::NUMERIC(10,2)) AS profit,
                    SUM(order_num::NUMERIC(10,2)) AS order_num,
                    SUM(sales_volume::NUMERIC(10,2)) AS sales_volume
                FROM
                    ddrs_cat_lv3_summary
                WHERE
                    cmid ={}
                AND
                    foreign_store_id = '{}'
                AND
                    date >= '{}'
                AND
                    date <= '{}'
                AND
                    id  != ''
                GROUP BY
                    year,
                    id
            """.format(cm_id, store_id, start, end)
        df = pandas.read_sql(select_query, RS_ENGINE)
        _dict = df.to_dict("records")
        return _dict

    @staticmethod
    def select_cat_lv4_day(cm_id, store_id, start, end):
        select_query = """
                SELECT
                    date,
                    id,
                    SUM(sales::NUMERIC(10,2)) AS sales,
                    SUM(profit::NUMERIC(10,2)) AS profit,
                    SUM(order_num::NUMERIC(10,2)) AS order_num,
                    SUM(sales_volume::NUMERIC(10,2)) AS sales_volume
                FROM
                    ddrs_cat_lv4_summary
                WHERE
                    cmid ={}
                AND
                    foreign_store_id = '{}'
                AND
                    date >= '{}'
                AND
                    date <= '{}'
                AND
                    id  != ''
                GROUP BY
                    date,
                    id
            """.format(cm_id, store_id, start, end)
        df = pandas.read_sql(select_query, RS_ENGINE)
        _dict = df.to_dict("records")
        return _dict

    @staticmethod
    def select_cat_lv4_month(cm_id, store_id, start, end):
        select_query = """
                SELECT
                    to_date(date, 'YYYY-MM-01') as month,
                    id,
                    SUM(sales::NUMERIC(10,2)) AS sales,
                    SUM(profit::NUMERIC(10,2)) AS profit,
                    SUM(order_num::NUMERIC(10,2)) AS order_num,
                    SUM(sales_volume::NUMERIC(10,2)) AS sales_volume
                FROM
                    ddrs_cat_lv4_summary
                WHERE
                    cmid ={}
                AND
                    foreign_store_id = '{}'
                AND
                    date >= '{}'
                AND
                    date <= '{}'
                AND
                    id  != ''
                GROUP BY
                    month,
                    id
            """.format(cm_id, store_id, start, end)
        df = pandas.read_sql(select_query, RS_ENGINE)
        _dict = df.to_dict("records")
        return _dict

    @staticmethod
    def select_cat_lv4_year(cm_id, store_id, start, end):
        select_query = """
                SELECT
                    EXTRACT(year from date) AS year,
                    id,
                    SUM(sales::NUMERIC(10,2)) AS sales,
                    SUM(profit::NUMERIC(10,2)) AS profit,
                    SUM(order_num::NUMERIC(10,2)) AS order_num,
                    SUM(sales_volume::NUMERIC(10,2)) AS sales_volume
                FROM
                    ddrs_cat_lv4_summary
                WHERE
                    cmid ={}
                AND
                    foreign_store_id = '{}'
                AND
                    date >= '{}'
                AND
                    date <= '{}'
                AND
                    id  != ''
                GROUP BY
                    year,
                    id
            """.format(cm_id, store_id, start, end)
        df = pandas.read_sql(select_query, RS_ENGINE)
        _dict = df.to_dict("records")
        return _dict

    @staticmethod
    def select_item_week_cat(cm_id, store_id, start, end):
        select_query = """
        SELECT
            cat_lv1_id,
            cat_lv1_name,
            cat_lv2_id,
            cat_lv2_name,
            cat_lv3_id,
            cat_lv3_name,
            cat_lv4_id,
            cat_lv4_name
        FROM
            ddrs_item_summary
        WHERE
            date >= '{}'
            AND 
            date <= '{}'
            AND
            cmid = {}
            AND
            foreign_store_id = '{}'
            AND
            cat_lv1_id !=''
        GROUP BY
            cat_lv1_id,
            cat_lv1_name,
            cat_lv2_id,
            cat_lv2_name,
            cat_lv3_id,
            cat_lv3_name,
            cat_lv4_id,
            cat_lv4_name
        """.format(start, end, cm_id, store_id)
        df = pandas.read_sql(select_query, RS_ENGINE)
        _dict = df.to_dict("records")

        return _dict

    @staticmethod
    def select_item_week_sku(cm_id, store_id, start, end):
        select_query = """
        SELECT
            cat_lv1_id,
            cat_lv2_id,
            cat_lv3_id,
            cat_lv4_id,
            price::NUMERIC(10,2) AS price,
            COUNT(DISTINCT item_id) AS sku_num
        FROM
            ddrs_item_summary
        WHERE
            date >= '{}'
        AND
            date <= '{}'
        AND
            cmid = {}
        AND
            foreign_store_id = '{}'
        AND
            cat_lv1_id !=''
        GROUP BY
            cat_lv1_id,
            cat_lv2_id,
            cat_lv3_id,
            cat_lv4_id,
            price
        ORDER BY
            price
        """.format(start, end, cm_id, store_id)

        df = pandas.read_sql(select_query, RS_ENGINE)
        _dict = df.to_dict("records")
        return _dict

    @staticmethod
    def select_item_week_price_band(cm_id, store_id, start, end):

        select_query = """
        SELECT 
            cat_lv1_id,
            cat_lv1_name,
            cat_lv2_id,
            cat_lv2_name,
            cat_lv3_id,
            cat_lv3_name,
            cat_lv4_id,
            cat_lv4_name,
            item_id,
            item_name,
            MIN(price::NUMERIC(10,2)) AS price,
            SUM(sales_volume::NUMERIC(10,2)) AS sales_volume,
            SUM(profit::NUMERIC(10,2)) AS profit,
            SUM(sales::NUMERIC(10,2)) AS sales
        FROM
            ddrs_item_summary
        WHERE
            date >= '{}'
        AND
            date <= '{}'
        AND
            cmid = {}
        AND
            foreign_store_id = '{}'
        AND
            cat_lv1_id !=''
        GROUP BY
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
        ORDER BY
            price
        """.format(start, end, cm_id, store_id)
        df = pandas.read_sql(select_query, RS_ENGINE)
        _dict = df.to_dict("records")
        return _dict

