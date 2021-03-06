from datetime import datetime


def utc_now():
    return datetime.utcnow()


def utc_now_str():
    return datetime2str(datetime.utcnow())


def now_timestamp_s():
    return int(datetime.now().timestamp())


def now_timestamp_ms():
    return int(datetime.now().timestamp() * 1000)


def utc_now_timestamp_s():
    return int(datetime.utcnow().timestamp())


def utc_now_timestamp_ms():
    return int(datetime.utcnow().timestamp() * 1000)


def datetime2str(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
