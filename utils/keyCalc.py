from hashlib import sha1
import hmac
from dotenv import dotenv_values
import os
import yaml
import utils.getConfig as getConfig

def getUrl(request):
    config = getConfig.getconfig()

    
    devId = int(config['ptv_api']['dev_id'])
    key = bytes(config['ptv_api']['dev_id'], "utf-8")
    request = request + ('&' if ('?' in request) else '?')
    raw = request + 'devid={0}'.format(devId)
    
    # Encode the raw string
    raw_encoded = raw.encode('utf-8')
    
    hashed = hmac.new(key, raw_encoded, sha1)
    signature = hashed.hexdigest()
    return 'http://timetableapi.ptv.vic.gov.au' + raw + '&signature={1}'.format(devId, signature)
