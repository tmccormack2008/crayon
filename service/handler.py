import json

from favicon_utils import getFaviconUrl


def handle_geturl(event, context):

    fav_url = getFaviconUrl('https://www.google.com')

    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(fav_url)
    }

    return response


# if __name__ == "__main__":
#     ico_url = getFaviconUrl('https://www.google.com')
#     print(ico_url)
  
#     ico_url = getFaviconUrl('')
#     print(ico_url)
  
#     ico_url = getFaviconUrl(None)
#     print(ico_url)
  
#     ico_url = getFaviconUrl('www.google.com')
#     print(ico_url)
  
#     ico_url = getFaviconUrl('https://www.dsfgsdf.com')
#     print(ico_url)
