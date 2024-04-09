import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

cik = '0000004977'

url = "https://data.sec.gov/submissions/CIK"+cik+".json"

headers = { # change the name of user
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
}

response = requests.get(url, headers=headers)
data = json.loads(response.text)

data_listings = pd.DataFrame()
for c in data['filings']['recent'].keys():
    data_listings[c] = data['filings']['recent'][c]

if 'files' in data['filings']:
    older_listings = data['filings']['files']

data_10q = data_df.loc[data_df['form']=='10-Q', :].copy()



