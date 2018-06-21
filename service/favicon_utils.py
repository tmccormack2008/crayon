import requests
from requests.exceptions import ConnectionError
from urllib import parse


FAVICON_TEXT = 'favicon.ico'

def getFaviconUrl(baseurl):
	
    if not baseurl:
        print(f'Missing baseurl')
        return None

    test_url = parse.urlsplit(baseurl)
    if not all([test_url.scheme, test_url.netloc]):
        print(f'Invalid baseurl {baseurl}')
        return None

    favicon_url = parse.urljoin(baseurl, FAVICON_TEXT)

    try:
    	resp = requests.get(favicon_url)
    except ConnectionError:
    	print(f'Unable to reach website {favicon_url}')
    	return None
    
    print(resp)

    if resp.status_code == 200:
        return favicon_url
    else:
        print(f'Favicon not found at {favicon_url}')
