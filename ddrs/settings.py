import sys
import boto3
from utilib.utils.dynamo import DynamoDBHelper
from os import environ
from os.path import abspath, dirname, join

DEBUG = environ.get('DEBUG') == 'True'

LISTEN_PORT = 8000

COOKIE_SECRET = 'CDCzNkbbQIixlRr+lqteEUddeDV8nkb7tfeRllhH4ME='

ROOT_DIR = dirname(abspath(__file__))

ENVS = {
    'TEST': {
        'host': environ.get('CM_DDRS_TEST_DB_HOST'),
        'user': environ.get('CM_DDRS_TEST_DB_USER'),
        'database': environ.get('CM_DDRS_TEST_DB_NAME'),
        'password': environ.get('CM_DDRS_TEST_DB_PASSWORD')
    },
    'PROD': {
        'host': environ.get('CM_DDRS_DB_HOST'),
        'user': environ.get('CM_DDRS_DB_USER'),
        'database': environ.get('CM_DDRS_DB_NAME'),
        'password': environ.get('CM_DDRS_DB_PASSWORD')
    }
}

if DEBUG:
    db = ENVS.get('TEST')

else:
    db = ENVS.get('PROD')

CM_REDSHIFT_DB_URL = environ.get('CM_REDSHIFT_DB_URL')
CM_CHAINSTORE_DB_URL = environ.get('CM_CHAINSTORE_DB_URL')

DB_USER = db.get('user')
DB_PASSWORD = db.get('password')
DB_DATABASE = db.get('database')
DB_HOST = db.get('host')
DB_CONN_POOL_MIN_SIZE = 10
DB_CONN_POOL_MAX_SIZE = 100

REDIS_HOST = environ.get('CM_REDIS_URL')
REDIS_PORT = environ.get('CM_REDIS_PORT')
REDIS_DB_INDEX = environ.get('CM_REDIS_CHAINSTORE_DB')
REDIS_CONN_POOL_MIN_SIZE = 20
REDIS_CONN_POOL_MAX_SIZE = 100

CELERY_DB = environ.get('CM_REDIS_CELERY_DB')
CELERY_BROKER = 'redis://chaomeng-business.zcllqp.0001' \
                '.cnn1.cache.amazonaws.com.cn:6379/13'

CACHES = {

    'default': {
        'cache': 'aiocache.RedisCache',
        'endpoint': REDIS_HOST,
        'port': REDIS_PORT,
        'db': 4,
        'timeout': 1,
        'serializer': {
            'class': 'aiocache.serializers.PickleSerializer'
        },
        'plugins': [
            {'class': 'aiocache.plugins.HitMissRatioPlugin'},
            {'class': 'aiocache.plugins.TimingPlugin'}
        ]
    }
}

SESSION_PREFIX = 'SESSION'
LOCK_PREFIX = 'lock'

CAPTCHA_CACHE_PREFIX = 'CAPTCHA'
CAPTCHA_TIMEOUT = 10 * 60
VCODE_CACHE_PREFIX = 'VCODE'
VCODE_TIMEOUT = 10 * 60

AWS_ACCESS_KEY_ID = environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = environ.get('AWS_SECRET_ACCESS_KEY')
LOGIN_URL = '/v0/login'

CM_GAODE_MAP_URL = 'http://restapi.amap.com/v3/geocode/geo'
GAODE_MAP_KEY = environ.get('GAODE_MAP_KEY')

dynamoDB_app = DynamoDBHelper(AWS_ACCESS_KEY_ID,
                              AWS_SECRET_ACCESS_KEY)
