import json
import time
import random
import requests
import pandas as pd

comp_list = pd.read_csv("files/000_desc.csv")
comp_list['CIK'] = comp_list['CIK'].apply(lambda x: str(x).zfill(10))

cik = '0000320193'

for cik in comp_list['CIK']:

    comp_name = comp_list.loc[comp_list['CIK'] == cik, 'Company name'].values[0]
    comp_ticker = comp_list.loc[comp_list['CIK'] == cik, 'Ticker'].values[0]

    url = "https://data.sec.gov/submissions/CIK"+cik+".json"

    headers = {
        "User-Agent": "National Technical University of Athens, PhD Researcher msolov@fsu.gr"
    }

    time.sleep(random.randint(1, 3))
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)

    data_filings = pd.DataFrame()

    for c in data['filings']['recent'].keys():
        data_filings[c] = data['filings']['recent'][c]

    if bool(data['filings']['files']):
        older_filings = data['filings']['files']

        ulr_older = "https://data.sec.gov/submissions/"+older_filings[0]['name']

        response = requests.get(ulr_older, headers=headers)
        data_old = json.loads(response.text)

        data_filings_old = pd.DataFrame()

        for c in data_old.keys():
            data_filings_old[c] = data_old[c]
        data_filings = pd.concat((data_filings, data_filings_old))
        print(comp_ticker, comp_name, cik, 'completed')

    path_filings = str('C:/Users/Marina/Documents/PhD/'+comp_ticker+'_filings.csv')
    # noinspection PyTypeChecker
    data_filings.to_csv(path_filings, index=False)
