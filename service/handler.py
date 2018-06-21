import json

from favicon_utils import getFaviconUrl


def handle_geturl(event, context):

    target = event['queryStringParameters']['target']

    status, ico_url, msg = getFaviconUrl(target)

    return_msg = ico_url if status == 200 else msg


    response = {
        "statusCode": status,
        "body": json.dumps(return_msg)
    }

    return response


if __name__ == "__main__":
    status, ico_url, msg = getFaviconUrl('https://www.google.com')
    print(status, ico_url, msg)

    status, ico_url, msg  = getFaviconUrl('https://www.google.com/tom')
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
