from kombu.utils.url import parse_url


def get_broker_transport(app):
    try:
        broker = parse_url(app.conf.broker_url)
        return broker.get('transport')
    except:
        return None
