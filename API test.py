import requests
import pandas as pd

client_id = 'AYbTsiF72D23YuW0cdORgA'
secret_key = 'wYNcSmwpReY3B4sVVhgTfPK3rW-EGA'
auth = requests.auth.HTTPBasicAuth(client_id, secret_key)

with open('pw.txt', 'r') as f:
    pw = f.read()

# login data
data = {'grant_type':'password',
        'username':'testlabsapi',
        'password':pw}

headers = {'User-Agent':'MyAPI/0.0.1'}

#request OAuth token
res = requests.post('https://www.reddit.com/api/v1/access_token',
                    auth=auth, data=data, headers=headers)

# token value from response
token = res.json()['access_token']

# add authorization to headers
headers['Authorization']=f"bearer{token}"

res = requests.get('https://oauth.reddit.com/api/v1/me',headers=headers)

res = requests.get('https://oauth.reddit.com/r/casual_conersation/hot',headers=headers)

print(headers)