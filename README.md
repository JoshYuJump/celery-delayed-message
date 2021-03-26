# celery-delayed-message
Real celery delayed message 

# Usage
## install
```shell
pip install celery_delayed_message
```
## add schedule into your beat_schedule
```
{
    'task': 'celery_delayed_message.redis_handlers.manager',
    'schedule': timedelta(hours=1),
}
```
## patch your task
```python
from celery_delayed_message import patch_celery_task

patch_celery_task()
```
