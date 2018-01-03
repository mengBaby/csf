from datetime import datetime
from uvtor.db import models
from uvtor.db.models.user import User
from playhouse.postgres_ext import IntegerField, CharField, \
    TextField, BooleanField, DateTimeField, ForeignKeyField, DecimalField


class ChainStore(models.BaseModel):

    cm_name = CharField(max_length=255,
                        verbose_name='连锁店名称')
    description = CharField(max_length=128,
                            verbose_name='连锁店描述',
                            null=True)
    create_date = DateTimeField(default=datetime.now(),
                                verbose_name='创建时间')
    last_update = DateTimeField(default=datetime.now(),
                                verbose_name='最后更新')
    use_standard_category = BooleanField(default=False,
                                         verbose_name='是否使用标准库品类')

    class Meta:
        db_table = 'chain_store'


class StoreType(models.BaseModel):
    type_name = CharField(max_length=64,
                          verbose_name='类型名称')

    class Meta:
        db_table = 'store_type'


class Store(models.BaseModel):
    # CASCADE 联动删除
    chain_store = ForeignKeyField(ChainStore,
                                  related_name='stores',
                                  on_delete='CASCADE',
                                  on_update='CASCADE')
    cm_id = IntegerField(index=True,
                         verbose_name='连锁ID')
    foreign_store_id = CharField(index=True, verbose_name='店铺ID')
    store_name = CharField(max_length=64,
                           verbose_name='店铺名称')
    store_address = TextField(null=True,
                              verbose_name='店铺地址')
    store_type = ForeignKeyField(StoreType,
                                 related_name='stores',
                                 on_delete='CASCADE',
                                 on_update='CASCADE')
    address_code = CharField(null=True,
                             verbose_name='地址代码')
    device_id = CharField(null=True,
                          verbose_name='设备码')

    create_date = DateTimeField(default=datetime.now(),
                                verbose_name='创建时间')
    last_update = DateTimeField(default=datetime.now(),
                                verbose_name='最后更新')
    store_status = BooleanField(default=True,
                                verbose_name='店铺状态')
    lat = DecimalField(null=True,
                       verbose_name='纬度')
    lng = DecimalField(null=True,
                       verbose_name='经度')

    class Meta:
        db_table = 'store'


class Role(models.BaseModel):
    role_name = CharField(max_length=64,
                          verbose_name='角色名')
    chain_store = ForeignKeyField(ChainStore,
                                  related_name='roles',
                                  on_delete='CASCADE',
                                  on_update='CASCADE')
    description = CharField(max_length=128,
                            verbose_name='描述',
                            null=True)
    create_date = DateTimeField(default=datetime.now(),
                                verbose_name='创建时间')
    last_update = DateTimeField(default=datetime.now(),
                                verbose_name='最后更新')

    class Meta:
        db_table = 'role'


class Area(models.BaseModel):
    area_name = CharField(max_length=64,
                          verbose_name='区域名称')
    pid = IntegerField(index=True,
                       default=0,
                       verbose_name='父级ID')
    is_end = BooleanField(index=True,
                          default=False,
                          verbose_name='是否是末端区域')
    chain_store = ForeignKeyField(ChainStore,
                                  related_name='areas',
                                  on_delete='CASCADE',
                                  on_update='CASCADE')
    level = IntegerField(index=True,
                         default=0,
                         verbose_name='当前层级数')
    description = CharField(max_length=128,
                            verbose_name='描述',
                            null=True)
    create_date = DateTimeField(default=datetime.now(),
                                verbose_name='创建时间')
    last_update = DateTimeField(default=datetime.now(),
                                verbose_name='最后更新')

    class Meta:
        db_table = 'area'


class StoreArea(models.BaseModel):
    store = ForeignKeyField(Store,
                            related_name='store_areas',
                            on_delete='CASCADE',
                            on_update='CASCADE')
    area = ForeignKeyField(Area,
                           related_name='store_areas',
                           on_delete='CASCADE',
                           on_update='CASCADE')

    class Meta:
        db_table = 'store_area'


class Menu(models.BaseModel):
    menu_name = CharField(max_length=64,
                          verbose_name='菜单名')
    description = CharField(max_length=128,
                            null=True,
                            verbose_name='菜单描述')


class RoleMenu(models.BaseModel):
    role = ForeignKeyField(Role,
                           related_name='role_menus',
                           on_delete='CASCADE',
                           on_update='CASCADE')
    menu = ForeignKeyField(Menu,
                           related_name='role_menus',
                           on_delete='CASCADE',
                           on_update='CASCADE')

    class Meta:
        db_table = 'role_menu'


class ChainUser(models.BaseModel):
    chain_store = ForeignKeyField(ChainStore,
                                  related_name='chain_users',
                                  on_delete='CASCADE',
                                  on_update='CASCADE')
    user = ForeignKeyField(User,
                           related_name='chain_users',
                           on_delete='CASCADE',
                           on_update='CASCADE')
    role_ids = CharField(max_length=128,
                         null=True,
                         verbose_name='用户角色')
    is_admin = BooleanField(default=False,
                            verbose_name='是否是管理员')

    class Meta:
        db_table = 'chain_user'


class UserArea(models.BaseModel):
    user = ForeignKeyField(User,
                           related_name='user_areas',
                           on_delete='CASCADE',
                           on_update='CASCADE')
    area = ForeignKeyField(Area,
                           related_name='user_areas',
                           on_delete='CASCADE',
                           on_update='CASCADE')

    class Meta:
        db_table = 'user_area'


class UserStore(models.BaseModel):
    user = ForeignKeyField(User,
                           related_name='user_stores',
                           on_delete='CASCADE',
                           on_update='CASCADE')
    store = ForeignKeyField(Store,
                            related_name='user_stores',
                            on_delete='CASCADE',
                            on_update='CASCADE')

    class Meta:
        db_table = 'user_store'


class Record(models.BaseModel):
    cm_id = IntegerField(verbose_name='连锁ID')
    foreign_store_id = IntegerField(verbose_name='店铺ID')
    date = CharField(max_length=128,
                     verbose_name='数据日期')
    last_update = DateTimeField(default=datetime.now(),
                                verbose_name='最后更新')

    class Meta:
        db_table = 'record'


class Category(models.BaseModel):
    cm_id = IntegerField(verbose_name='连锁ID')
    level = IntegerField(index=True,
                         default=0,
                         verbose_name='层级数')
    foreign_category_lv1 = CharField(max_length=20,
                                     verbose_name='一级分类ID',
                                     null=True)
    foreign_category_lv1_name = CharField(max_length=20,
                                          verbose_name='一级分类名称',
                                          null=True)
    foreign_category_lv2 = CharField(max_length=20,
                                     verbose_name='二级分类ID',
                                     null=True)
    foreign_category_lv2_name = CharField(max_length=20,
                                          verbose_name='二级分类名称',
                                          null=True)
    foreign_category_lv3 = CharField(max_length=20,
                                     verbose_name='三级分类ID',
                                     null=True)
    foreign_category_lv3_name = CharField(max_length=20,
                                          verbose_name='三级分类名称',
                                          null=True)
    foreign_category_lv4 = CharField(max_length=20,
                                     verbose_name='四级分类ID',
                                     null=True)
    foreign_category_lv4_name = CharField(max_length=20,
                                          verbose_name='四级分类名称',
                                          null=True)
    last_update = DateTimeField(default=datetime.now(),
                                verbose_name='最后更新')

    class Meta:
        db_table = 'category'
