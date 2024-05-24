import requests
import time
import random
import re
from bs4 import BeautifulSoup
import pandas as pd
from sec_downloader import Downloader
dl = Downloader("MyCompanyName", "email@example.com")
from sec_api.cleaning_functions import htm_cleaner

comp_list = pd.read_csv("C:/Users/Marina/Documents/PhD/Data/Financials/000_desc.csv")
comp_list['CIK'] = comp_list['CIK'].apply(lambda x: str(x).zfill(10))

cik = '0000004977'

comp_name = comp_list.loc[comp_list['CIK'] == cik, 'Company name'].values[0]
comp_ticker = comp_list.loc[comp_list['CIK'] == cik, 'Ticker'].values[0]

path_filings = str('C:/Users/Marina/Documents/PhD/Data/Financials/' + comp_ticker + '_filings.csv')
comp_filings = pd.read_csv(path_filings)

list_10q = list(comp_filings.loc[comp_filings['form'] == '10-Q', 'accessionNumber'])

comp_t1 = pd.DataFrame()
comp_t2 = pd.DataFrame()
comp_t3 = pd.DataFrame()

for filing in list_10q:
    print(filing)
    acn = filing.replace('-', '')
    doc = comp_filings.loc[comp_filings['accessionNumber'] == filing, 'primaryDocument'].values[0]

    url = 'https://www.sec.gov/Archives/edgar/data/' + cik + '/' + acn + '/' + doc
    print(url)

    headers = {
        "User-Agent": "National Technical University of Athens, PhD Researcher msolov@fsu.gr"
    }

    time.sleep(random.randint(1, 2))
    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")
    hop = [span.get_text().lower() for span in soup.find_all('span')]

    target_table = pd.DataFrame

    if url[-3:] == 'htm':
        target_table = htm_cleaner(soup)
    else:
        print(url[-3:], filing, url)

    if not comp_t1.empty:
        target_table.drop_duplicates(subset='Name', inplace=True)
        comp_t1.drop_duplicates(subset='Name', inplace=True)
        comp_t1 = pd.merge(comp_t1, target_table, on='Name', how='outer', suffixes=('', '_new'))
        comp_t1 = comp_t1[[col for col in comp_t1.columns if not col.endswith('_new')]]
    else:
        target_table.drop_duplicates(subset='Name', inplace=True)
        comp_t1.drop_duplicates(subset='Name', inplace=True)
        comp_t1 = target_table.copy()

