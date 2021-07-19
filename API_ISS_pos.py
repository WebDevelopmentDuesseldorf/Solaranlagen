import requests
res = requests.get('http://api.open-notify.org/iss-now.json')
if res:
    print('Latitude: '+ res.json()['iss_position']['latitude'])
else:
    print('Response Failed')
