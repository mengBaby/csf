import pandas
from utils.engine_config import RS_ENGINE
from sqlalchemy import text


def is_exist_in_summary(chain_store_id,
                        store_id,
                        record_date,
                        table_name):
    """
    判断是否存在与summary
    :param chain_store_id:
    :param store_id:
    :param record_date:
    :param table_name:
    :return:
    """
    select_query = """
        SELECT
            date
        FROM
            {}
        WHERE
            cmid = {}
        AND
            foreign_store_id = '{}'
        AND
            date = '{}'
        LIMIT 1
    """.format(table_name,
               chain_store_id,
               store_id,
               record_date)
    df_select = pandas.read_sql(select_query, RS_ENGINE)
    if df_select.empty:
        return False
    return True


def delete_data(chain_store_id,
                store_id,
                start,
                end,
                table_name):
    delete_query = """
        DELETE FROM {}
        WHERE
            date >= '{}'
        AND
            date <= '{}'
        AND
            cmid = {}
        AND
            foreign_store_id = '{}'
    """.format(table_name,
               start,
               end,
               chain_store_id,
               store_id)
    RS_ENGINE.execute(text(delete_query))
    return True
