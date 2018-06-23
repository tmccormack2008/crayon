#!/usr/bin/python
# coding: utf-8
import json

from favicon_utils import getFaviconUrl
from icondb import IconDB


def handle_geturl(event, context):

    target = event['queryStringParameters']['target']

    status, ico_url, msg = getFaviconUrl(target)

    return_msg = ico_url if status == 200 else msg

    response = {
        "statusCode": status,
        "body": json.dumps(return_msg)
    }

    return response


def handle_geticondb(event, context):

    host = 'crayon-postgres.coghvekvxrjf.us-east-1.rds.amazonaws.com'
    port = 5432
    database = 'favicon'
    user = 'crayon'
    password = 'Crayonpw99'

    icondb = IconDB(host, port, database, user, password)

    print(icondb)

    response = {
        "statusCode": 200,
        "body": json.dumps("it worked")
    }

    return response
