# 启动方式
# celery -A tasks worker --loglevel=info
from celery import Celery
import pkgutil
import redis
from uvtor.conf import settings
import eventlet
# eventlet.monkey_patch()

celery_app = Celery('tasks', broker=settings.CELERY_BROKER)
_redis_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB_INDEX
)

redis_client = redis.StrictRedis(connection_pool=_redis_pool)
__import__('tasks')


def auto_discover():
    _tasks = __import__('tasks')
    for loader, module_name, is_pkg in pkgutil.walk_packages(_tasks.__path__):
        loader.find_module(module_name).load_module(module_name)


auto_discover()


celery_app.conf.beat_schedule = {

}
