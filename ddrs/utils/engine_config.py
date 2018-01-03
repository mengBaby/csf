
from sqlalchemy import create_engine
from uvtor.conf import settings

RS_ENGINE = create_engine(settings.CM_REDSHIFT_DB_URL)
CHAIN_STORE_ENGINE = create_engine(settings.CM_CHAINSTORE_DB_URL)
