from config import *
from celery import Celery
from celery.schedules import crontab

# 定时
app = Celery('tasks', broker=CELERY_RESULT_BACKEND)
celery_time = crontab(minute=CELERY_TIME)

app.conf.beat_schedule = {
    'main-every': {
        'task': 'haiwai.main',
        'schedule': celery_time,
    },
}
