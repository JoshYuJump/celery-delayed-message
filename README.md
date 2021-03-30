# celery-delayed-message
Real celery delayed message 

# Usage
## install
```shell
pip install celery_delayed_message
```
## patch your task
```python
from celery_delayed_message import patch_celery_task

patch_celery_task()
```
## settings
```python
from datetime import timedelta

DELAY = {
    "delay_time_at_least": timedelta(hours=2),  # default is 2 hours
}
```
