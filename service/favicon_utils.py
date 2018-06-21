import requests
from requests.exceptions import ConnectionError
from urllib import parse


FAVICON_TEXT = 'favicon.ico'

def getFaviconUrl(target_url):
	
    if not target_url:
        print(f'Missing target url')
        return None

    temp_url = parse.urlsplit(target_url, scheme='https')
    print(temp_url)

    # if we don't have either a netloc or a path component, bail
    if not temp_url.netloc and not temp_url.path:
        print(f'Invalid target url {target_url}')
        return None

    base_url = ''
    if temp_url.netloc:
    	base_url = '{0}://{1}'.format(temp_url.scheme, temp_url.netloc)
    else:
    	base_url = '{0}://{1}'.format(temp_url.scheme, temp_url.path)
    print(base_url)

    favicon_url = parse.urljoin(base_url, FAVICON_TEXT)

    try:
    	resp = requests.get(favicon_url)
    except ConnectionError:
    	print(f'Unable to reach website {base_url}')
    	return None
    
    print(resp)

    if resp.status_code == 200:
        return favicon_url
    else:
        print(f'Favicon not found at {favicon_url}')
