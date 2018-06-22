#!/usr/bin/python
# coding: utf-8
import requests
from requests.exceptions import ConnectionError
from urllib import parse


FAVICON_TEXT = 'favicon.ico'

def getFaviconUrl(target_url):
	
    if not target_url:
        msg = f'Missing target url'
        return 400, None, msg

    temp_url = parse.urlsplit(target_url, scheme='http')

    # if we don't have either a netloc or a path component, bail
    if not temp_url.netloc and not temp_url.path:
        msg = f'Invalid target url {target_url}'
        return 400, None, msg

    base_url = ''
    if temp_url.netloc:
    	base_url = '{0}://{1}'.format(temp_url.scheme, temp_url.netloc)
    else:
    	base_url = '{0}://{1}'.format(temp_url.scheme, temp_url.path)

    favicon_url = parse.urljoin(base_url, FAVICON_TEXT)

    try:
    	resp = requests.get(favicon_url)
    except ConnectionError:
    	msg = f'Unable to reach website {base_url}'
    	return 404, None, msg

    if resp.status_code == 200:
        return 200, favicon_url, ''
    else:
        msg = f'Favicon not found at {favicon_url}'
        return resp.status_code, None, msg


if __name__ == "__main__":
    status, ico_url, msg = getFaviconUrl('https://www.google.com')
    print(status, ico_url, msg)

    status, ico_url, msg  = getFaviconUrl('https://www.google.com/tom')
    print(status, ico_url, msg)

    status, ico_url, msg  = getFaviconUrl('www.google.com/index.html')
    print(status, ico_url, msg)
  
    status, ico_url, msg  = getFaviconUrl('https://www.google.com:443/dick')
    print(status, ico_url, msg)
   
    status, ico_url, msg  = getFaviconUrl('')
    print(status, ico_url, msg)
  
    status, ico_url, msg  = getFaviconUrl(None)
    print(status, ico_url, msg)
  
    status, ico_url, msg  = getFaviconUrl('www.google.com')
    print(status, ico_url, msg)
  
    status, ico_url, msg  = getFaviconUrl('https://www.dsfgsdf.com')
    print(status, ico_url, msg)
