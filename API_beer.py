# import requests, pandas
import requests
import pandas as pd

# Parameter für Biere die zu Lachs passen
parameters = {
    'food_pairing': 'salmon',
    'abv_gt':10
}

# request
res = requests.get('https://api.punkapi.com/v2/beers',params=parameters)

# IDs ausgeben
if res:
    df = pd.DataFrame(data=res.json())
    df = df[['id','abv','name','food_pairing']].sort_values(by='abv')
    print(df.head(5))
else:
    print('Response Failed')