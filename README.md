# celery-delayed-message

Real celery delayed message 

# Usage

## install

```shell
pip install celery-delayed-message
```

## patch your task

```python
from celery_delayed_message import monkey
monkey.path()
```

# Settings

## `delay`

Countdown/ETA tasks delayed seconds greater then `delay` settings, will be processed by celery-delayed-message.

Default value: 3600 (seconds)
