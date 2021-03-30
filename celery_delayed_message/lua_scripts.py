from celery._state import connect_on_app_finalize
from celery.utils.log import get_logger
from kombu.utils import symbol_by_name

from .helpers import using_redis_transport, install_default_entries
from .redis_clients import set_connection_url

logger = get_logger(__name__)


@connect_on_app_finalize
def init_celery_delayed_message(app):
    if using_redis_transport(app):
        logger.info("init celery delayed message")

        set_connection_url(app.conf.broker_url)
        scheduler = symbol_by_name(app.conf.beat_scheduler)
        scheduler.install_default_entries = install_default_entries
