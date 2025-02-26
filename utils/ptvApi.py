from hashlib import sha1
import hmac
import requests
import asyncio
import aiohttp


def getUrl(request):
    devId = 3002809
    key = bytes('9edbf794-4a92-43c2-9459-70c6f65fcae1', "utf-8")
    request = request + ('&' if ('?' in request) else '?')
    raw = request + 'devid={0}'.format(devId)
    
    # Encode the raw string
    raw_encoded = raw.encode('utf-8')
    
    hashed = hmac.new(key, raw_encoded, sha1)
    signature = hashed.hexdigest()
    return 'http://timetableapi.ptv.vic.gov.au' + raw + '&signature={1}'.format(devId, signature)

async def get_async(session, request):
    url = getUrl(request)
    async with session.get(url) as response:
        if response.status == 200:
            return await response.json()
        else:
            print(f"Error: {response.status} - {await response.text()}")
            return None


def get(request):
    url = getUrl(request)
    response = requests.get(url)
    if response.status_code == 200:
        # Parse and work with the response data (assuming it's JSON)
        data = response.json()
        return data

    else:
        # Print an error message if the request was not successful
        print(f"Error: {response.status_code} - {response.text}")
        return