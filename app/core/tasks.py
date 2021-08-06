import time

from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone

logger = get_task_logger(__name__)


@shared_task
def wait_seconds(total):
    logger.info('Starting...')
    time.sleep(total)
    return "Encerrado as {}".format(timezone.now())