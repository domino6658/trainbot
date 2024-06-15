from hashlib import sha1
import hmac
from dotenv import dotenv_values
import os
import yaml
import utils.getConfig as getConfig


def getUrl(request):
    config = getConfig.getconfig()

    devId = int(config['ptv_api']['dev_id'])
    key = str(config['ptv_api']['dev_id'])
    
    request = request + ('&' if ('?' in request) else '?')
    raw = request+'devid={0}'.format(devId)
    hashed = hmac.new(key, raw, sha1)
    signature = hashed.hexdigest()

    return 'http://timetableapi.ptv.vic.gov.au' + raw + '&signature={1}'.format(devId, signature)
