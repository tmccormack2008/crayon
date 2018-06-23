#!/usr/bin/python
# coding: utf-8
import requests
from requests.exceptions import ConnectionError
from urllib import parse

from icondb import IconDB


FAVICON_TEXT = 'favicon.ico'


def getIconDBParams():

    # setup function so we can pull from SSM later
    params = {'host': 'crayon-postgres.coghvekvxrjf.us-east-1.rds.amazonaws.com',
              'port': 5432,
              'database': 'favicon',
              'user': 'crayon',
              'password': 'Crayonpw99',
              }

    return params


def getIconDBConn(params):
    return IconDB(params['host'], params['port'], params['database'], params['user'], params['password'])


def getFaviconUrlFromRow(row):
    return row[2]


def getFaviconUrl(target_url):

    if not target_url:
        msg = f'Missing target url'
        return 400, None, msg

    temp_url = parse.urlsplit(target_url, scheme='http')

    # if we don't have either a netloc or a path component, bail
    if not temp_url.netloc and not temp_url.path:
        msg = f'Invalid target url {target_url}'
        return 400, None, msg

    # check database here and return if found and has icon url
    icondb = getIconDBConn(getIconDBParams())
    row = icondb.read_row(target_url)
    update_row = False
    if row:
        favicon_url = getFaviconUrlFromRow(row)
        if favicon_url:
            return 200, favicon_url, ''
        else:
            update_row = True

    # build favicon url anv check if it exists
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

    if resp.status_code == 200:  # use 'is good' function from requests
        if update_row:
            icondb.update_favicon_url_row(target_url, favicon_url)
        else:
            icondb.create_row(target_url, favicon_url)
        return 200, favicon_url, ''
    else:
        msg = f'Favicon not found at {favicon_url}'
        return resp.status_code, None, msg


if __name__ == "__main__":

    # host = 'crayon-postgres.coghvekvxrjf.us-east-1.rds.amazonaws.com'
    # # host = 'localhost'
    # port = 5432
    # database = 'favicon'
    # user = 'crayon'
    # password = 'Crayonpw99'

    # icondb = IconDB(host, port, database, user, password)

    # icondb.create_table()

    # icondb.delete_table()

    print(getFaviconUrl('www.google.com'))
    print(getFaviconUrl('www.google.com/index.html'))
    print(getFaviconUrl('http://www.google.com'))
    print(getFaviconUrl('https://www.google.com'))
    print(getFaviconUrl('aaa'))
    print(getFaviconUrl('ggg'))
    print(getFaviconUrl('www.aadsf.com'))
    print(getFaviconUrl('www.yahoo.com/index.html'))
    print(getFaviconUrl('www.si.com'))
