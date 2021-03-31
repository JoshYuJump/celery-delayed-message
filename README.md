# celery-delayed-message
Real celery delayed message 

# Usage
## install
```shell
pip install celery_delayed_message
```
## patch your task in main.py and celeryconfig.py
```python
from celery_delayed_message import monkey
monkey.patch()
```
## optional settings
```python
from datetime import timedelta

DELAY = {
    "delay_time_at_least": timedelta(hours=2),  # default is 2 hours
}
```
## for Redis broker, pls enable your celery beat, cache manager will run every hour.
