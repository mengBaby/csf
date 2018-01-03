from uvtor.core.decorators.api import standard_api
from ddrs.apps.listen.handlers import BaseHandler
from ddrs.tasks.tasks import gen_need_data


class ListenQueueHandler(BaseHandler):

    @standard_api
    async def get(self):
        """

        :return:
        """
        return {
            'msg': 'get success'
        }

    @standard_api
    async def post(self):
        """
        :return:
        """
        # TODO
        # 监听队列，用celery 跑数据
        chain_store_id = self.get_argument('chain_store_id')
        gen_need_data.delay(chain_store_id)
        return {
            'msg': ' post success'
        }
