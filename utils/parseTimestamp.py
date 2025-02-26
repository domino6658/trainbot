from datetime import datetime

def parse_timestamp(timestamp):
    return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
