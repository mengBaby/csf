from uvtor.core.decorators.api import standard_api
from uvtor.db.models import manager
from apps.report.handlers import BaseHandler
from models.model import UserStore, ChainUser, RoleMenu, Store
from utils.auth import login_required
import pandas
import json


class StoreHandler(BaseHandler):
    @standard_api
    @login_required
    async def get(self):
        user = await self.get_current_user()
        if user.is_superuser:
            user = self.get_cookie('userId')
        flag = True
        user_stores = await manager.execute(
            UserStore.select().join(Store).where(UserStore.user == user,
                                                 Store.store_status == flag))
        response = []
        for user_store in user_stores:
            dict = {}
            dict['id'] = user_store.store.id
            dict['name'] = user_store.store.store_name
            dict['cm_id'] = user_store.store.cm_id
            dict['foreign_store_id'] = user_store.store.foreign_store_id
            response.append(dict)
        return {'data': response}


class MenuHandler(BaseHandler):
    @standard_api
    @login_required
    async def get(self):
        user = await self.get_current_user()
        if user.is_superuser:
            user = self.get_cookie('userId')
        chain_user = await manager.get(
            ChainUser.select().where(ChainUser.user == user))
        role_ids = chain_user.role_ids.split(',')
        menus = await manager.execute(
            RoleMenu.select().where(RoleMenu.role << role_ids))
        response = []
        for menu in menus:
            menu_dict = {}
            menu_dict['id'] = menu.menu.id
            menu_dict['description'] = menu.menu.description
            menu_dict['route'] = menu.menu.menu_name
            response.append(menu_dict)
        response = [dict(t) for t in set([tuple(d.items()) for d in response])]
        response = pandas.read_json(json.dumps(response))
        response.sort_values(by=['id'], ascending=[1], inplace=True)
        return {'data': response.to_dict('records')}
