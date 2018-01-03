from uvtor.core.decorators.api import standard_api
from uvtor.db.models import manager
from uvtor.db.models.user import User
from apps.manage.handlers import BaseHandler
from utils.auth import login_required
from utils.auth import sys_admin_required
from utils.auth import admin_required
from models import model
from playhouse.shortcuts import model_to_dict
from uvtor.core import exceptions
from utils.ddrs_utils import address_to_location
from utils import ddrs_utils as dus
from datetime import datetime
from utilib.utils import timezone
from utils.time_utils import get_today_str
from tasks.tasks import gen_dynamodb_data, gen_everyday_summary
from peewee import JOIN
import json
import logging


async def get_chain_user(user):
    chain_user = await manager.get(
        model.ChainUser.select().where(model.ChainUser.user == user))
    return chain_user


class ChainStoreHandler(BaseHandler):
    @standard_api
    @sys_admin_required
    async def get(self):
        chain_stores = await manager.execute(model.ChainStore.select())
        chain_list = []
        flag = True
        for chain_store in chain_stores:
            chain = model_to_dict(chain_store)
            store_num = len(await manager.execute(model.Store.select().where(
                model.Store.chain_store == chain_store,
                model.Store.store_status == flag)))
            chain['store_num'] = store_num
            chain['create_date'] = timezone.cst(chain['create_date'])
            chain['last_update'] = timezone.cst(chain['last_update'])
            chain_list.append(chain)
        return {'data': chain_list}

    @standard_api
    @sys_admin_required
    async def post(self):
        chain_name = self.get_argument('chainName')
        use_standard = self.get_argument('useStandard', 'false') == 'true'
        chain_store = await manager.execute(model.ChainStore.select().where(
            model.ChainStore.cm_name == chain_name))
        if chain_store:
            raise exceptions.ObjectAlreadyExists
        else:
            chain_id = await manager.execute(
                model.ChainStore.insert(
                    cm_name=chain_name, use_standard_category=use_standard))
        return {'data': {'chainId': chain_id}}

    @standard_api
    @sys_admin_required
    async def patch(self):
        chain_id = int(self.get_argument('chainId'))
        use_standard = self.get_argument('useStandard', 'false') == 'true'
        chain_name = self.get_argument('chainName', '')
        if chain_name == '':
            chain_name = await manager.get(model.ChainStore.select().where(
                model.ChainStore.id == chain_id))
        await manager.execute(
            model.ChainStore.update(
                cm_name=chain_name.cm_name,
                use_standard_category=use_standard,
                last_update=datetime.now()).where(
                    model.ChainStore.id == chain_id))


class StoreTypeHandler(BaseHandler):
    @standard_api
    @login_required
    async def get(self):
        types = await manager.execute(model.StoreType.select())
        type_list = [model_to_dict(type) for type in types]
        return {'data': type_list}

    @standard_api
    @sys_admin_required
    async def post(self):
        type_name = self.get_argument('type')
        type = await manager.execute(model.StoreType.select().where(
            model.StoreType.type_name == type_name))
        if type:
            raise exceptions.ObjectAlreadyExists
        else:
            await manager.execute(model.StoreType.insert(type_name=type_name))


class StoreHandler(BaseHandler):
    @standard_api
    @login_required
    async def get(self):
        per_page = None
        page = None
        search = None
        user = await self.get_current_user()
        if user.is_superuser:
            chain_id = self.get_argument('chainId')
        else:
            per_page = self.get_argument('per_page', None)
            page = self.get_argument('page', None)
            search = self.get_argument('search', None)
            chain_user = await get_chain_user(user)
            chain_id = chain_user.chain_store.id
        chain_store = await manager.get(
            model.ChainStore.select().where(model.ChainStore.id == chain_id))
        if search:
            search = "%" + search + "%"
            stores = await manager.execute(model.Store.select().where(
                model.Store.store_name % search,
                model.Store.chain_store == chain_store))
        else:
            flag = True
            stores = await manager.execute(model.Store.select().where(
                model.Store.chain_store == chain_store,
                model.Store.store_status == flag))

        response = {}
        if per_page and page:
            per_page = int(per_page)
            page = int(page)
            if len(stores) % per_page == 0:
                response['pages'] = len(stores) // per_page
            else:
                response['pages'] = len(stores) // per_page + 1
            stores = stores[(page - 1) * per_page:page * per_page]
        response['chainName'] = chain_store.cm_name
        response['storeList'] = {}
        storeList = response['storeList']
        for store in stores:
            if store.store_type.id not in storeList:
                storeList[store.store_type.id] = {}
            storeList[store.store_type.id][
                'type_name'] = store.store_type.type_name
            storeList[store.store_type.id]['type_id'] = store.store_type.id
            if 'infoList' in storeList[store.store_type.id]:
                info_list = storeList[store.store_type.id]['infoList']
            else:
                info_list = []
            info = {
                'type_name': store.store_type.type_name,
                'id': store.id,
                'cmid': store.cm_id,
                'foreignStoreId': store.foreign_store_id,
                'name': store.store_name,
                'address': store.store_address
            }
            info_list.append(info)
            storeList[store.store_type.id]['infoList'] = info_list
        return {'data': response}

    @standard_api
    @admin_required
    async def post(self):
        chain_store_id = self.get_argument('chainId')
        store_list = self.get_argument('storeList')
        store_list = json.loads(store_list)
        for store_info in store_list:
            try:
                store_type = int(store_info['type'])
            except BaseException:
                raise exceptions.MissingRequiredParams
            info_list = store_info['infoList']
            for info in info_list:
                address = info['address']
                lat, lng, address_code = address_to_location(address)
                if 'id' not in info:
                    await manager.execute(
                        model.Store.insert(
                            chain_store=chain_store_id,
                            store_type=store_type,
                            cm_id=info['cmid'],
                            foreign_store_id=info['foreignStoreId'],
                            store_name=info['name'],
                            store_address=address,
                            lat=lat,
                            lng=lng,
                            address_code=address_code))
                else:
                    await manager.execute(
                        model.Store.update(
                            chain_store=chain_store_id,
                            store_type=store_type,
                            cm_id=info['cmid'],
                            foreign_store_id=info['foreignStoreId'],
                            store_name=info['name'],
                            store_address=address,
                            lat=lat,
                            lng=lng,
                            address_code=address_code).where(
                                model.Store.id == info['id']))

    @standard_api
    @admin_required
    async def delete(self):
        store_id = int(self.get_argument('id'))
        store = await manager.get(
            model.Store.select().where(model.Store.id == store_id))
        store.store_status = False
        store.save()
        return {'data': 'success'}


class MenuAllHandler(BaseHandler):
    @standard_api
    @admin_required
    async def get(self):
        menus = await manager.execute(model.Menu.select())
        menu_list = [model_to_dict(menu) for menu in menus]
        return {'data': menu_list}


class UserStatusHandler(BaseHandler):
    @standard_api
    @admin_required
    async def post(self):
        user_id = self.get_argument('userId')
        is_active = self.get_argument('isActive') == 'true'
        await manager.execute(
            User.update(is_active=is_active, ).where(model.User.id == user_id))


class UserBasicInfoHandler(BaseHandler):
    # @standard_api
    # @login_required
    # async def get(self):
    #     user_id = self.get_argument('userId')
    #     user = User.get(id=user_id)
    #     response = dus.get_user_basic_info(user)
    #     return {'data': response}

    @standard_api
    @login_required
    async def post(self):
        user_id = self.get_argument('userId')
        _username = self.get_argument('username', '')
        _phone = self.get_argument('phone', None)
        _email = self.get_argument('email', None)
        name = self.get_argument('name', None)
        await manager.execute(
            User.update(
                username=_username,
                phone=_phone,
                email=_email,
                first_name=name).where(User.id == user_id))

    @standard_api
    @login_required
    async def patch(self):
        user_id = self.get_argument('userId', None)
        if not user_id:
            old_password = self.get_argument('old_password', None)
            user = await self.get_current_user()
            user.check_password(old_password)
            user_id = user.id
        password = self.get_argument('password')
        user = User.get(id=user_id)
        await user._set_password(password)


class ChainUserHandler(BaseHandler):
    @standard_api
    @sys_admin_required
    async def get(self, **kwargs):
        user_list = []
        users = await manager.execute(model.ChainUser.select().where(
            model.ChainUser.is_admin))

        for user in users:
            user_dict = {}
            user_dict['userId'] = user.user.id
            user_dict['username'] = user.user.username
            user_dict['chainId'] = user.chain_store.id
            user_dict['chainName'] = user.chain_store.cm_name
            user_dict['createDate'] = timezone.cst(user.user.date_joined)
            user_dict['isActive'] = user.user.is_active
            user_dict['userId'] = user.user.id
            user_dict['lastLogin'] = ''
            if user.user.last_login:
                user_dict['lastLogin'] = timezone.cst(user.user.last_login)
            user_list.append(user_dict)
        return {'data': user_list}

    @standard_api
    async def post(self):
        _username = self.get_argument('username', '')
        _password = self.get_argument('password', '')
        _phone = self.get_argument('phone', None)
        _email = self.get_argument('email', None)
        _first_name = self.get_argument('firstName', '')
        _last_name = self.get_argument('lastName', '')
        chain_id = self.get_argument('chainId')
        menus = self.get_argument('selectedMenu')
        menus = json.loads(menus)

        await User.validate(
            phone=_phone,
            username=_username,
            email=_email,
            raise_exception=True)
        _id = await User.create_user(
            username=_username,
            password=_password,
            phone=_phone,
            email=_email,
            first_name=_first_name,
            last_name=_last_name)

        _user = User.get(id=_id)
        roles = await manager.execute(model.Role.select().where(
            model.Role.chain_store == chain_id,
            model.Role.role_name == '系统管理员'))

        if len(roles) == 0:
            role_id = await manager.execute(
                model.Role.insert(role_name='系统管理员', chain_store=chain_id))
            for menu_id in menus:
                menu = await manager.get(model.Menu.get(id=menu_id))
                await manager.execute(
                    model.RoleMenu.insert(role=role_id, menu=menu))
        else:
            role = roles[0]
            role_id = role.id

        await manager.execute(
            model.ChainUser.insert(
                chain_store=chain_id,
                user=_user,
                role_ids=str(role_id),
                is_admin=True))


class ChainStoreMenuHandler(BaseHandler):
    @standard_api
    @sys_admin_required
    async def get(self):
        user_id = self.get_argument('userId')
        chain_user = await get_chain_user(user_id)
        role = await manager.get(model.Role.select().where(
            model.Role.chain_store_id == chain_user.chain_store,
            model.Role.role_name == '系统管理员'))
        menus = await manager.execute(
            model.RoleMenu.select().where(model.RoleMenu.role == role))
        response = {}
        response['username'] = chain_user.user.username
        response['chainName'] = chain_user.chain_store.cm_name
        response['chainId'] = chain_user.chain_store.id
        menu_list = []
        for menu in menus:
            menu_list.append(model_to_dict(menu.menu))
        menu_list = [
            dict(t) for t in set([tuple(d.items()) for d in menu_list])
        ]
        response['selectedMenu'] = menu_list
        return {'data': response}

    @standard_api
    @sys_admin_required
    async def post(self):
        chain_id = self.get_argument('chainId')
        menus = self.get_argument('selectedMenu')
        menus = json.loads(menus)
        role = await manager.get(model.Role.select().where(
            model.Role.chain_store_id == chain_id,
            model.Role.role_name == '系统管理员'))
        await manager.execute(
            model.RoleMenu.delete().where(model.RoleMenu.role == role))
        for menu_id in menus:
            await manager.execute(
                model.RoleMenu.insert(role=role, menu=menu_id))


class UserMenuHandler(BaseHandler):
    @standard_api
    @login_required
    async def get(self):
        user = await self.get_current_user()
        user_menu_list = []
        chain_user = await get_chain_user(user)
        role_ids = chain_user.role_ids.split(',')
        for role_id in role_ids:
            menus = await manager.execute(
                model.RoleMenu.select().where(model.RoleMenu.role == role_id))
            for menu in menus:
                user_menu = {}
                user_menu['id'] = menu.menu.id
                user_menu['name'] = menu.menu.menu_name
                user_menu['description'] = menu.menu.description
                user_menu_list.append(user_menu)
        user_menu_list = [
            dict(t) for t in set([tuple(d.items()) for d in user_menu_list])
        ]
        return {'data': user_menu_list}


class StoreRoleHandler(BaseHandler):
    @standard_api
    @admin_required
    async def get(self):
        user = await self.get_current_user()
        chain_user = await get_chain_user(user)
        roles = await manager.execute(model.Role.select().where(
            model.Role.chain_store == chain_user.chain_store).order_by(
                model.Role.create_date))
        response = []
        for role in roles:
            dict = {}
            dict['role_id'] = role.id
            dict['role_name'] = role.role_name
            dict['description'] = role.description
            dict['create_date'] = timezone.cst(role.create_date)
            dict['last_update'] = timezone.cst(role.last_update)
            response.append(dict)
        return {'data': response}


class RoleMenuHandler(BaseHandler):
    @standard_api
    @admin_required
    async def get(self):
        role_id = self.get_argument('role_id')
        role = await manager.get(
            model.Role.select().where(model.Role.id == role_id))
        response = {}
        response['role_id'] = role.id
        response['role_name'] = role.role_name
        response['description'] = role.description
        response['create_date'] = timezone.cst(role.create_date)
        response['last_update'] = timezone.cst(role.last_update)
        response['menus'] = []
        menus = await manager.execute(
            model.RoleMenu.select().where(model.RoleMenu.role == role_id))
        for menu in menus:
            response['menus'].append(model_to_dict(menu.menu))
        return {'data': response}

    @standard_api
    @admin_required
    async def post(self):
        user = await self.get_current_user()
        chain_user = await get_chain_user(user)
        role_name = self.get_argument('name')
        description = self.get_argument('description')
        menu_ids = json.loads(self.get_argument('menu_ids'))
        role_id = await manager.execute(
            model.Role.insert(
                role_name=role_name,
                chain_store=chain_user.chain_store,
                description=description))
        for menu_id in menu_ids:
            await manager.execute(
                model.RoleMenu.insert(role=role_id, menu=menu_id))

    @standard_api
    @admin_required
    async def patch(self):
        role_id = self.get_argument('id')
        role_name = self.get_argument('name')
        description = self.get_argument('description')
        menu_ids = json.loads(self.get_argument('menu_ids'))
        await manager.execute(
            model.Role.update(
                role_name=role_name,
                description=description,
                last_update=datetime.now()).where(model.Role.id == role_id))
        await manager.execute(
            model.RoleMenu.delete().where(model.RoleMenu.role == role_id))
        for menu_id in menu_ids:
            await manager.execute(
                model.RoleMenu.insert(role=role_id, menu=menu_id))

    @standard_api
    @admin_required
    async def delete(self):
        role_id = self.get_argument('id')
        await manager.execute(
            model.Role.delete().where(model.Role.id == role_id))


class ChainAreaHandler(BaseHandler):
    @standard_api
    @admin_required
    async def get(self):
        user = await self.get_current_user()
        chain_user = await get_chain_user(user)
        areas = await manager.execute(model.Area.select().where(
            model.Area.chain_store == chain_user.chain_store).order_by(
                model.Area.id))
        areas = dus.gen_area(areas)
        return {'data': areas}


class AreaStoreHandler(BaseHandler):
    @standard_api
    @admin_required
    async def get(self):
        area_id = self.get_argument('area_id')
        area = await manager.get(
            model.Area.select().where(model.Area.id == area_id))
        response = {}
        response['area_id'] = area.id
        response['area_name'] = area.area_name
        response['pid'] = area.pid
        response['is_end'] = area.is_end
        response['description'] = area.description
        response['create_date'] = timezone.cst(area.create_date)
        response['last_update'] = timezone.cst(area.last_update)
        response['store_ids'] = []
        response['pname'] = ''
        if area.pid != 0:
            response['pname'] = model.Area.get(id=area.pid).area_name
        stores = await manager.execute(
            model.StoreArea.select().where(model.StoreArea.area == area_id))
        for store in stores:
            response['store_ids'].append(store.store.id)
        return {'data': response}

    @standard_api
    @admin_required
    async def post(self):
        user = await self.get_current_user()
        area_name = self.get_argument('name')
        description = self.get_argument('description')
        store_ids = json.loads(self.get_argument('store_ids'))
        pid = int(self.get_argument('pid', 0))
        is_end = self.get_argument('is_end', 'false') == 'true'
        chain_user = await get_chain_user(user)
        if pid == 0:
            level = 1
        else:
            try:
                parea = await manager.get(
                    model.Area.select().where(model.Area.id == pid))
            except BaseException:
                parea = None
            if not parea:
                raise exceptions.InvalidParameterValue
            level = parea.level + 1
        area_id = await manager.execute(
            model.Area.insert(
                area_name=area_name,
                chain_store=chain_user.chain_store,
                description=description,
                pid=pid,
                is_end=is_end,
                level=level))
        for store_id in store_ids:
            await manager.execute(
                model.StoreArea.insert(area=area_id, store=store_id))

    @standard_api
    @admin_required
    async def patch(self):
        user = await self.get_current_user()
        chain_user = await get_chain_user(user)
        area_id = self.get_argument('id')
        area_name = self.get_argument('name')
        description = self.get_argument('description')
        store_ids = json.loads(self.get_argument('store_ids'))
        pid = int(self.get_argument('pid', 0))
        is_end = self.get_argument('is_end', 'false') == 'true'
        if pid == 0:
            level = 1
        else:
            level = model.Area.get(id=pid).level + 1
        await manager.execute(
            model.Area.update(
                area_name=area_name,
                chain_store=chain_user.chain_store,
                description=description,
                pid=pid,
                is_end=is_end,
                level=level,
                last_update=datetime.now()).where(model.Area.id == area_id))
        await manager.execute(
            model.StoreArea.delete().where(model.StoreArea.area == area_id))
        for store_id in store_ids:
            await manager.execute(
                model.StoreArea.insert(area=area_id, store=store_id))

    @standard_api
    @admin_required
    async def delete(self):
        area_id = self.get_argument('id')
        await manager.execute(
            model.Area.delete().where((model.Area.id == area_id)
                                      | (model.Area.pid == area_id)))


class UserHandler(BaseHandler):
    @standard_api
    @admin_required
    async def get(self):
        user = await self.get_current_user()
        per_page = int(self.get_argument('per_page', 20))
        page = int(self.get_argument('page', 1))
        status = int(self.get_argument('status', 0))
        choose_role = int(self.get_argument('role', 0))
        user_search = self.get_argument('user_search', None)
        chain_user = await get_chain_user(user)
        chain_store = chain_user.chain_store
        if status == 0:
            if user_search:
                user_search = "%" + user_search + "%"
                users = await manager.execute(
                    model.ChainUser.select().join(User).where(
                        (model.ChainUser.chain_store == chain_store),
                        ((User.username % user_search)
                         | (User.phone % user_search)
                         | (User.email % user_search)
                         | (User.first_name % user_search))))
            else:
                users = await manager.execute(model.ChainUser.select().where(
                    model.ChainUser.chain_store == chain_store).order_by(
                        model.ChainUser.id))
        else:
            _is_active = status == 1
            if user_search:
                user_search = "%" + user_search + "%"
                users = await manager.execute(
                    model.ChainUser.select().join(User).where(
                        ((User.is_active == _is_active),
                         (model.ChainUser.chain_store == chain_store),
                         ((User.username % user_search)
                          | (User.phone % user_search)
                          | (User.email % user_search)
                          | (User.first_name % user_search)))))
            else:
                users = await manager.execute(
                    model.ChainUser.select().join(User).where(
                        User.is_active == _is_active,
                        model.ChainUser.chain_store == chain_store).order_by(
                            model.ChainUser.id))
        response = {}
        response['userList'] = []
        if len(users) % per_page == 0:
            response['pages'] = len(users) // per_page
        else:
            response['pages'] = len(users) // per_page + 1
        users = users[(page - 1) * per_page:page * per_page]
        for user in users:
            role_ids = user.role_ids.split(',')
            role_ids = [int(t) for t in role_ids]
            if choose_role != 0:
                if choose_role not in role_ids:
                    continue
            role_name = ''
            for role_id in role_ids:
                try:
                    role = await manager.get(
                        model.Role.select().where(model.Role.id == role_id))
                    role_name += role.role_name + ','
                except BaseException:
                    continue
            role_name = role_name.strip(',')
            dict = {}
            dict['user_id'] = user.user.id
            dict['is_manager'] = user.is_admin
            dict['user_login_name'] = user.user.username
            dict['user_name'] = user.user.first_name
            dict['user_phone'] = user.user.phone
            dict['user_email'] = user.user.email
            dict['user_role'] = role_name
            dict['user_role_id_list'] = role_ids
            dict['user_create_time'] = timezone.cst(user.user.date_joined)
            dict['user_last_login_time'] = ''
            if user.user.last_login:
                dict['user_last_login_time'] = timezone.cst(
                    user.user.last_login)
            dict['user_status'] = user.user.is_active
            dict['selected_area_list'] = []
            dict['selected_store_list'] = []
            areas = await manager.execute(
                model.UserArea.select().where(model.UserArea.user == user.user)
            )
            for area in areas:
                area_dict = {}
                area_dict['id'] = area.area.id
                area_dict['name'] = area.area.area_name
                dict['selected_area_list'].append(area_dict)
            stores = await manager.execute(model.UserStore.select().where(
                model.UserStore.user == user.user))
            for store in stores:
                dict['selected_store_list'].append(store.store.id)
            response['userList'].append(dict)
        return {'data': response}

    @standard_api
    @admin_required
    async def post(self):
        user = await self.get_current_user()
        chain_user = await get_chain_user(user)
        username = self.get_argument('login_name', '')
        password = self.get_argument('password', '')
        phone = self.get_argument('phone', None)
        email = self.get_argument('email', None)
        first_name = self.get_argument('name', None)
        role_ids = json.loads(self.get_argument('role_list', None))
        areas_ids = json.loads(self.get_argument('area_list', None))
        store_ids = json.loads(self.get_argument('store_list', None))
        if not store_ids:
            store_ids = []
        if email == '':
            email = None
        await User.validate(
            phone=phone, username=username, email=email, raise_exception=True)
        user_id = await User.create_user(
            username=username,
            password=password,
            phone=phone,
            email=email,
            first_name=first_name)
        role_str = ''
        for role_id in role_ids:
            role_str += str(role_id) + ','
        await manager.execute(
            model.ChainUser.insert(
                chain_store=chain_user.chain_store,
                user=user_id,
                role_ids=role_str.strip(',')))
        for area_id in areas_ids:
            await manager.execute(
                model.UserArea.insert(user=user_id, area=area_id))
            stores = await manager.execute(
                model.StoreArea.select().where(
                    model.StoreArea.area == area_id
                )
            )
            for store in stores:
                store_ids.append(store.store.id)
        store_ids = set(store_ids)
        for store_id in store_ids:
            await manager.execute(
                model.UserStore.insert(user=user_id, store=store_id))

    @standard_api
    @admin_required
    async def patch(self):
        user_id = self.get_argument('user_id')
        role_ids = json.loads(self.get_argument('role_list', None))
        areas_ids = json.loads(self.get_argument('area_list', None))
        store_ids = json.loads(self.get_argument('store_list', None))
        if not store_ids:
            store_ids = []
        role_str = ''
        for role_id in role_ids:
            role_str += str(role_id) + ','
        await manager.execute(
            model.ChainUser.update(role_ids=role_str.strip(',')).where(
                model.ChainUser.user == user_id))
        await manager.execute(
            model.UserArea.delete().where(model.UserArea.user == user_id))
        await manager.execute(
            model.UserStore.delete().where(model.UserStore.user == user_id))
        for area_id in areas_ids:
            await manager.execute(
                model.UserArea.insert(user=user_id, area=area_id))
            stores = await manager.execute(
                model.StoreArea.select().where(
                    model.StoreArea.area == area_id
                )
            )
            for store in stores:
                store_ids.append(store.store.id)
        store_ids = set(store_ids)
        for store_id in store_ids:
            await manager.execute(
                model.UserStore.insert(user=user_id, store=store_id))


class UpdateHandler(BaseHandler):
    @standard_api
    @admin_required
    async def post(self):
        store_id = self.get_argument('id')
        store = await manager.get(
            model.Store.select().where(model.Store.id == store_id))
        start = '2016-01-01'
        end = get_today_str(days=-1)
        gen_everyday_summary.apply_async(
            (store.cm_id, store.foreign_store_id, start, end),
            link=gen_dynamodb_data.s(store.cm_id, store.foreign_store_id,
                                     start, end))
        return {'data': 'success'}


class UpdateStoreHandler(BaseHandler):
    @standard_api
    @admin_required
    async def post(self):
        user = await self.get_current_user()
        store_info = self.get_argument('storeInfo')
        store_info = json.loads(store_info)
        address = store_info['address']
        lat, lng, address_code = address_to_location(address)
        store = await manager.get(
            model.Store.select().where(model.Store.id == store_info['id']))
        store.cm_id = store_info['cmId']
        store.foreign_store_id = store_info['foreignStoreId']
        store.store_address = address
        store.lat = lat
        store.lng = lng
        store.address_code = address_code
        store.store_name = store_info['storeName']
        store.save()
        return {'data': 'success'}


class ChainStoreInfoHandler(BaseHandler):
    @standard_api
    @admin_required
    async def get(self):
        args_name = self.get_argument('searchName', None)
        if args_name:
            args_name = '%' + args_name + '%'
            user_data = await manager.execute(model.ChainUser.select().where(
                model.ChainUser.user << User.select(User.id).where(
                    User.username % args_name)))
            if not user_data:
                user_data = await manager.execute(
                    model.ChainUser.select().where(
                        model.ChainUser.chain_store << model.ChainStore.select(
                            model.ChainStore.id).where(
                                model.ChainStore.cm_name % args_name)))
            if not user_data:
                user_data = await manager.execute(
                    model.ChainUser.select().where(
                        model.ChainUser.user << User.select(User.id).where(
                            User.first_name % args_name)))
        else:
            user_data = await manager.execute(model.ChainUser.select())
        areas = await manager.execute(model.UserArea.select())
        roles = await manager.execute(model.Role.select())
        role_dict = {}
        for role in roles:
            role_dict[role.id] = role.role_name

        user_dict = {}
        for cu in user_data:
            user_dict[cu.user.id] = None
            for i in cu.role_ids.split(','):
                if user_dict[cu.user.id]:
                    user_dict[cu.user.id] = role_dict[int(
                        i)] + ',' + user_dict[cu.user.id]
                else:
                    user_dict[cu.user.id] = role_dict[int(i)]

        area_dict = {}
        for area in areas:
            area_dict[area.user] = area.area.area_name
        data_dict = {}
        data_list = []
        for data in user_data:
            data_dict[data.user.id] = {
                'user_id':
                data.user.id,
                'username':
                data.user.username,
                'is_admin':
                data.is_admin,
                'first_name':
                data.user.first_name,
                'date_joined':
                data.user.date_joined.strftime('%Y-%m-%d %H:%M:%S')
                if data.user.date_joined else None,
                'is_superuser':
                data.user.is_superuser,
                'last_login':
                data.user.last_login.strftime('%Y-%m-%d %H:%M:%S')
                if data.user.last_login else None,
                'cm_name':
                data.chain_store.cm_name,
                'role_name':
                None,
                'area':
                None
            }
            if data.user.id in area_dict:
                data_dict[data.user.id]['area'] = area_dict[data.user.id]
            if data.user.id in user_dict:
                data_dict[data.user.id]['role_name'] = user_dict[data.user.id]
            data_list.append(data_dict[data.user.id])

        return {'data': data_list}
