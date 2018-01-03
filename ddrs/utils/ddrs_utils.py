from uvtor.conf import settings
from uvtor.db.models import manager
from uvtor.core import exceptions
from utilib.utils import timezone
from models.model import UserStore, Store
import requests
import json
import time


def address_to_location(address):
    """
    地址转换经纬度
    :param address
    :return lat, lng, adcode
    """
    url = settings.CM_GAODE_MAP_URL
    params = {"key": settings.GAODE_MAP_KEY, 'address': address}
    retry = 3
    while retry > 0:
        try:
            req = requests.get(url, params=params)
            json_data = json.loads(req.content)
            if json_data['info'] == 'OK' and len(json_data['geocodes']) > 0:
                geocodes = json_data['geocodes'][0]
                location = geocodes['location']
                adcode = geocodes.get('adcode')
                lat = float(location.split(',')[1])
                lng = float(location.split(',')[0])
                retry = -1
                return lat, lng, adcode
            else:
                time.sleep(0.5)
                retry = retry - 1
        except requests.RequestException as e:
            retry = retry - 1
    return None, None, None


def gen_area(areas):
    """
    区域无限分级
    :param data:
    :return:
    """
    node_list = []
    entries = {}
    for area in areas:
        entries[area.id] = entry = {
            'id': area.id,
            'pid': area.pid,
            'label': area.area_name,
            'is_end': area.is_end,
            'level': area.level,
            'description': area.description,
            'create_date': timezone.cst(area.create_date),
            'last_update': timezone.cst(area.last_update)
        }
        if area.pid == 0 or area.pid not in entries:
            node_list.append(entry)
        else:
            parent = entries[area.pid]
            parent.setdefault('children', []).append(entry)
    return node_list


def gen_category_lv4(data):
    """
    获取分类 四级
    :param data:
    :return:
    """
    _cat = {}
    temp_list = []
    for i in data:
        key_lv1 = i.foreign_category_lv1.strip(
        ) if i.foreign_category_lv1 else i.foreign_category_lv1
        key_lv2 = i.foreign_category_lv2.strip(
        ) if i.foreign_category_lv2 else i.foreign_category_lv2
        key_lv3 = i.foreign_category_lv3.strip(
        ) if i.foreign_category_lv3 else i.foreign_category_lv3
        key_lv4 = i.foreign_category_lv4.strip(
        ) if i.foreign_category_lv4 else i.foreign_category_lv4

        if key_lv1:
            if len(key_lv1) != 0:
                if key_lv1 not in _cat:
                    _cat[key_lv1] = {}
                    temp_dict = {
                        'label': i.foreign_category_lv1_name.strip(),
                        'id': i.foreign_category_lv1.strip(),
                        'level': 1
                    }
                    temp_list.append((key_lv1, 0, temp_dict))
                    _cat[key_lv1]['children'] = {}

        if key_lv1 and key_lv2:
            if len(key_lv1) != 0 and len(key_lv2) != 0:
                if key_lv2 not in _cat[key_lv1]['children']:
                    _cat[key_lv1]['children'][key_lv2] = {}
                    temp_dict = {
                        'label': i.foreign_category_lv2_name.strip(),
                        'id': i.foreign_category_lv2.strip(),
                        'level': 2
                    }
                    temp_list.append((key_lv2, key_lv1, temp_dict))
                    _cat[key_lv1]['children'][key_lv2]['children'] = {}

        if key_lv1 and key_lv2 and key_lv3:
            if len(key_lv1) != 0 and len(key_lv2) != 0 and len(key_lv3) != 0:
                if key_lv3 not in _cat[key_lv1]['children'][key_lv2][
                        'children']:
                    _cat[key_lv1]['children'][key_lv2]['children'][
                        key_lv3] = {}
                    temp_dict = {
                        'label': i.foreign_category_lv3_name.strip(),
                        'id': i.foreign_category_lv3.strip(),
                        'level': 3
                    }
                    temp_list.append((key_lv3, key_lv2, temp_dict))
                    _cat[key_lv1]['children'][key_lv2]['children'][key_lv3][
                        'children'] = {}
        if key_lv1 and key_lv2 and key_lv3 and key_lv4:
            if len(key_lv1) != 0 and len(key_lv2) != 0 and len(
                    key_lv3) != 0 and len(key_lv4) != 0:
                if key_lv4 not in _cat[key_lv1]['children'][key_lv2][
                        'children'][key_lv3]['children']:
                    _cat[key_lv1]['children'][key_lv2]['children'][key_lv3][
                        'children'][key_lv4] = {}
                    temp_dict = {
                        'label': i.foreign_category_lv4_name.strip(),
                        'id': i.foreign_category_lv4.strip(),
                        'level': 4
                    }
                    temp_list.append((key_lv4, key_lv3, temp_dict))

    cat_data = gen_category(temp_list)

    return cat_data


def gen_category_lv3(data):
    """
    获取分类
    :param data:
    :return:
    """
    _cat = {}
    temp_list = []
    for i in data:
        key_lv1 = i.foreign_category_lv1.strip(
        ) if i.foreign_category_lv1 else i.foreign_category_lv1
        key_lv2 = i.foreign_category_lv2.strip(
        ) if i.foreign_category_lv2 else i.foreign_category_lv2
        key_lv3 = i.foreign_category_lv3.strip(
        ) if i.foreign_category_lv3 else i.foreign_category_lv3
        if key_lv1:
            if len(key_lv1) != 0:
                if key_lv1 not in _cat:
                    _cat[key_lv1] = {}
                    temp_dict = {
                        'label': i.foreign_category_lv1_name.strip(),
                        'id': i.foreign_category_lv1.strip(),
                        'level': 1
                    }
                    temp_list.append((key_lv1, 0, temp_dict))
                    _cat[key_lv1]['children'] = {}

        if key_lv1 and key_lv2:
            if len(key_lv1) != 0 and len(key_lv2) != 0:
                if key_lv2 not in _cat[key_lv1]['children']:
                    _cat[key_lv1]['children'][key_lv2] = {}
                    temp_dict = {
                        'label': i.foreign_category_lv2_name.strip(),
                        'id': i.foreign_category_lv2.strip(),
                        'level': 2
                    }
                    temp_list.append((key_lv2, key_lv1, temp_dict))
                    _cat[key_lv1]['children'][key_lv2]['children'] = {}

        if key_lv1 and key_lv2 and key_lv3:
            if len(key_lv1) != 0 and len(key_lv2) != 0 and len(key_lv3) != 0:
                if key_lv3 not in _cat[key_lv1]['children'][key_lv2][
                        'children']:

                    _cat[key_lv1]['children'][key_lv2]['children'][
                        key_lv3] = {}
                    temp_dict = {
                        'label': i.foreign_category_lv3_name.strip(),
                        'id': i.foreign_category_lv3.strip(),
                        'level': 3
                    }
                    temp_list.append((key_lv3, key_lv2, temp_dict))
    cat_data = gen_category(temp_list)
    return cat_data


def gen_category_lv2(data):
    """
    获取分类
    :param data:
    :return:
    """
    cat = {}
    temp_list = []
    for i in data:
        key_lv1 = i.foreign_category_lv1.strip(
        ) if i.foreign_category_lv1 else i.foreign_category_lv1
        key_lv2 = i.foreign_category_lv2.strip(
        ) if i.foreign_category_lv2 else i.foreign_category_lv2
        if key_lv1:
            if len(key_lv1) != 0:
                if key_lv1 not in cat:
                    cat[key_lv1] = {}
                    temp_dict = {
                        'label': i.foreign_category_lv1_name.strip(),
                        'id': i.foreign_category_lv1.strip(),
                        'level': 1
                    }
                    temp_list.append((key_lv1, 0, temp_dict))
                    cat[key_lv1]['children'] = {}
        if key_lv2:
            if len(key_lv1) != 0 and len(key_lv2) != 0:
                if key_lv2 not in cat[key_lv1]['children']:
                    cat[key_lv1]['children'][key_lv2] = {}
                    temp_dict = {
                        'label': i.foreign_category_lv2_name.strip(),
                        'id': i.foreign_category_lv2.strip(),
                        'level': 2
                    }
                    temp_list.append((key_lv2, key_lv1, temp_dict))

    cat_data = gen_category(temp_list)

    return cat_data


def gen_category(data):
    """
    区域无限分级
    :param data:
    :return:
    """
    node_list = []
    entries = {}
    for cat in data:
        entries[cat[0]] = entry = {
            'id': cat[0],
            # 'pid': cat[1],
            'label': cat[2]['label'],
            'level': cat[2]['level'],
        }
        if cat[1] == 0 or cat[1] not in entries:
            node_list.append(entry)
        else:
            parent = entries[cat[1]]
            parent.setdefault('children', []).append(entry)
    return node_list


async def get_store_info(user, store_id):
    if user.is_superuser:
        store = await manager.get(Store.select().where(Store.id == store_id))
        return store.cm_id, store.foreign_store_id
    else:
        try:
            flag = True
            user_store = await manager.get(
                UserStore.select().join(Store).where(
                    UserStore.user == user, UserStore.store == store_id,
                    Store.store_status == flag))
        except BaseException:
            raise exceptions.PermissionDenied
        cm_id = user_store.store.cm_id
        foreign_store_id = user_store.store.foreign_store_id
        return cm_id, foreign_store_id
