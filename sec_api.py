import requests
import time
import random
import re
from bs4 import BeautifulSoup
import pandas as pd
from sec_downloader import Downloader
dl = Downloader("MyCompanyName", "email@example.com")
from functions_data_cleaning import clean_table, find_index, find_index_item

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
    acn = filing.replace('-', '')
    doc = comp_filings.loc[comp_filings['accessionNumber'] == filing, 'primaryDocument'].values[0]

    url = 'https://www.sec.gov/Archives/edgar/data/' + cik + '/' + acn + '/' + doc

    headers = {
        "User-Agent": "National Technical University of Athens, PhD Researcher msolov@fsu.gr"
    }

    time.sleep(random.randint(1, 3))
    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")
    hop = [span.get_text().lower() for span in soup.find_all('span')]

    tables = soup.find_all('table')

    dataframes_dict = {}

    for i, table in enumerate(tables[0:10]):
        rows = table.find_all('tr')
        table_data = []
        for row in rows:
            cells = row.find_all(['th', 'td'])
            row_data = []
            for cell in cells:
                cell_text = cell.get_text(strip=True)
                if cell_text and cell_text != '$':
                    row_data.append(cell_text)
            if row_data:
                table_data.append(row_data)

        df = pd.DataFrame(table_data)
        dataframes_dict[f"table_{i + 1}"] = df

    # Access each DataFrame using the keys in the dictionary
    # for key, df in dataframes_dict.items():
    #     print(f"DataFrame {key}:")
    #     print(df)

    target_table_key = None

    for key, df in dataframes_dict.items():
        if 'Total investments and cash' in df.values:
            target_table_key = key
            break

    if target_table_key:
        target_table = dataframes_dict[target_table_key]
        # Process target_table as needed
        print(f"Target table found in DataFrame {target_table_key}:")
        print(target_table)
    else:
        print("No table with 'Total investments and cash' found.")
