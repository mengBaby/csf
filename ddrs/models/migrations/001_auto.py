import datetime
import peewee as pw

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass


def migrate(migrator, database, fake=False, **kwargs):
    """Write your migrations here."""

    @migrator.create_model
    class ChainStore(pw.Model):
        cm_name = pw.CharField(max_length=255)
        description = pw.CharField(max_length=128, null=True)
        create_date = pw.DateTimeField(
            default=datetime.datetime(
                2017, 10, 26, 14, 32, 0, 838245))
        last_update = pw.DateTimeField(
            default=datetime.datetime(
                2017, 10, 26, 14, 32, 0, 838257))
        use_standard_category = pw.BooleanField(default=False)

        class Meta:
            db_table = "chain_store"

    @migrator.create_model
    class Area(pw.Model):
        area_name = pw.CharField(max_length=64)
        pid = pw.IntegerField(default=0, index=True)
        is_end = pw.BooleanField(default=False, index=True)
        chain_store = pw.ForeignKeyField(
            db_column='chain_store_id',
            on_delete='CASCADE',
            on_update='CASCADE',
            rel_model=migrator.orm['chain_store'],
            related_name='areas',
            to_field='id')
        level = pw.IntegerField(default=0, index=True)
        description = pw.CharField(max_length=128, null=True)
        create_date = pw.DateTimeField(
            default=datetime.datetime(
                2017, 10, 26, 14, 32, 0, 841004))
        last_update = pw.DateTimeField(
            default=datetime.datetime(
                2017, 10, 26, 14, 32, 0, 841015))

        class Meta:
            db_table = "area"

    @migrator.create_model
    class Category(pw.Model):
        cm_id = pw.IntegerField()
        level = pw.IntegerField(default=0, index=True)
        foreign_category_lv1 = pw.CharField(max_length=20, null=True)
        foreign_category_lv1_name = pw.CharField(max_length=20, null=True)
        foreign_category_lv2 = pw.CharField(max_length=20, null=True)
        foreign_category_lv2_name = pw.CharField(max_length=20, null=True)
        foreign_category_lv3 = pw.CharField(max_length=20, null=True)
        foreign_category_lv3_name = pw.CharField(max_length=20, null=True)
        foreign_category_lv4 = pw.CharField(max_length=20, null=True)
        foreign_category_lv4_name = pw.CharField(max_length=20, null=True)
        last_update = pw.DateTimeField(
            default=datetime.datetime(
                2017, 10, 26, 14, 32, 0, 843809))

        class Meta:
            db_table = "category"

    @migrator.create_model
    class User(pw.Model):
        date_joined = pw.DateTimeField(
            default=datetime.datetime(
                2017, 10, 26, 14, 32, 0, 837483))
        email = pw.CharField(max_length=255, null=True, unique=True)
        first_name = pw.CharField(max_length=255, null=True)
        is_active = pw.BooleanField(default=True)
        is_superuser = pw.BooleanField(default=False)
        last_login = pw.DateTimeField(null=True)
        last_name = pw.CharField(max_length=255, null=True)
        password = pw.CharField(max_length=255)
        salt = pw.CharField(max_length=255)
        phone = pw.CharField(max_length=255, null=True)
        username = pw.CharField(max_length=255, unique=True)

        class Meta:
            db_table = "_user"

    @migrator.create_model
    class ChainUser(pw.Model):
        chain_store = pw.ForeignKeyField(
            db_column='chain_store_id',
            on_delete='CASCADE',
            on_update='CASCADE',
            rel_model=migrator.orm['chain_store'],
            related_name='chain_users',
            to_field='id')
        user = pw.ForeignKeyField(
            db_column='user_id',
            on_delete='CASCADE',
            on_update='CASCADE',
            rel_model=migrator.orm['_user'],
            related_name='chain_users',
            to_field='id')
        role_ids = pw.CharField(max_length=128, null=True)
        is_admin = pw.BooleanField(default=False)

        class Meta:
            db_table = "chain_user"

    @migrator.create_model
    class Menu(pw.Model):
        menu_name = pw.CharField(max_length=64)
        description = pw.CharField(max_length=128, null=True)

        class Meta:
            db_table = "menu"

    @migrator.create_model
    class Record(pw.Model):
        cm_id = pw.IntegerField()
        foreign_store_id = pw.IntegerField()
        date = pw.CharField(max_length=128)
        last_update = pw.DateTimeField(
            default=datetime.datetime(
                2017, 10, 26, 14, 32, 0, 843415))

        class Meta:
            db_table = "record"

    @migrator.create_model
    class Role(pw.Model):
        role_name = pw.CharField(max_length=64)
        chain_store = pw.ForeignKeyField(
            db_column='chain_store_id',
            on_delete='CASCADE',
            on_update='CASCADE',
            rel_model=migrator.orm['chain_store'],
            related_name='roles',
            to_field='id')
        description = pw.CharField(max_length=128, null=True)
        create_date = pw.DateTimeField(
            default=datetime.datetime(
                2017, 10, 26, 14, 32, 0, 840572))
        last_update = pw.DateTimeField(
            default=datetime.datetime(
                2017, 10, 26, 14, 32, 0, 840584))

        class Meta:
            db_table = "role"

    @migrator.create_model
    class RoleMenu(pw.Model):
        role = pw.ForeignKeyField(
            db_column='role_id',
            on_delete='CASCADE',
            on_update='CASCADE',
            rel_model=migrator.orm['role'],
            related_name='role_menus',
            to_field='id')
        menu = pw.ForeignKeyField(
            db_column='menu_id',
            on_delete='CASCADE',
            on_update='CASCADE',
            rel_model=migrator.orm['menu'],
            related_name='role_menus',
            to_field='id')

        class Meta:
            db_table = "role_menu"

    @migrator.create_model
    class StoreType(pw.Model):
        type_name = pw.CharField(max_length=64)

        class Meta:
            db_table = "store_type"

    @migrator.create_model
    class Store(pw.Model):
        chain_store = pw.ForeignKeyField(
            db_column='chain_store_id',
            on_delete='CASCADE',
            on_update='CASCADE',
            rel_model=migrator.orm['chain_store'],
            related_name='stores',
            to_field='id')
        cm_id = pw.IntegerField(index=True)
        foreign_store_id = pw.CharField(index=True, max_length=255)
        store_name = pw.CharField(max_length=64)
        store_address = pw.TextField(null=True)
        store_type = pw.ForeignKeyField(
            db_column='store_type_id',
            on_delete='CASCADE',
            on_update='CASCADE',
            rel_model=migrator.orm['store_type'],
            related_name='stores',
            to_field='id')
        address_code = pw.CharField(max_length=255, null=True)
        device_id = pw.CharField(max_length=255, null=True)
        create_date = pw.DateTimeField(
            default=datetime.datetime(
                2017, 10, 26, 14, 32, 0, 838909))
        last_update = pw.DateTimeField(
            default=datetime.datetime(
                2017, 10, 26, 14, 32, 0, 838920))
        store_status = pw.BooleanField(default=True)
        lat = pw.DecimalField(
            auto_round=False,
            decimal_places=5,
            max_digits=10,
            null=True,
            rounding='ROUND_HALF_EVEN')
        lng = pw.DecimalField(
            auto_round=False,
            decimal_places=5,
            max_digits=10,
            null=True,
            rounding='ROUND_HALF_EVEN')

        class Meta:
            db_table = "store"

    @migrator.create_model
    class StoreArea(pw.Model):
        store = pw.ForeignKeyField(
            db_column='store_id',
            on_delete='CASCADE',
            on_update='CASCADE',
            rel_model=migrator.orm['store'],
            related_name='store_areas',
            to_field='id')
        area = pw.ForeignKeyField(
            db_column='area_id',
            on_delete='CASCADE',
            on_update='CASCADE',
            rel_model=migrator.orm['area'],
            related_name='store_areas',
            to_field='id')

        class Meta:
            db_table = "store_area"

    @migrator.create_model
    class UserArea(pw.Model):
        user = pw.ForeignKeyField(
            db_column='user_id',
            on_delete='CASCADE',
            on_update='CASCADE',
            rel_model=migrator.orm['_user'],
            related_name='user_areas',
            to_field='id')
        area = pw.ForeignKeyField(
            db_column='area_id',
            on_delete='CASCADE',
            on_update='CASCADE',
            rel_model=migrator.orm['area'],
            related_name='user_areas',
            to_field='id')

        class Meta:
            db_table = "user_area"

    @migrator.create_model
    class UserStore(pw.Model):
        user = pw.ForeignKeyField(
            db_column='user_id',
            on_delete='CASCADE',
            on_update='CASCADE',
            rel_model=migrator.orm['_user'],
            related_name='user_stores',
            to_field='id')
        store = pw.ForeignKeyField(
            db_column='store_id',
            on_delete='CASCADE',
            on_update='CASCADE',
            rel_model=migrator.orm['store'],
            related_name='user_stores',
            to_field='id')

        class Meta:
            db_table = "user_store"


def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

    migrator.remove_model('user_store')

    migrator.remove_model('user_area')

    migrator.remove_model('store_area')

    migrator.remove_model('store')

    migrator.remove_model('store_type')

    migrator.remove_model('role_menu')

    migrator.remove_model('role')

    migrator.remove_model('record')

    migrator.remove_model('menu')

    migrator.remove_model('chain_user')

    migrator.remove_model('_user')

    migrator.remove_model('category')

    migrator.remove_model('area')

    migrator.remove_model('chain_store')
