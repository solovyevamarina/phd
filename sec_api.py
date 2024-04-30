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

    time.sleep(random.randint(1, 2))
    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")
    hop = [span.get_text().lower() for span in soup.find_all('span')]

    tables = soup.find_all('table')

    tables_dict = {}

    for i, table in enumerate(tables[0:25]):
        rows = table.find_all('tr')
        table_data = []
        for row in rows:
            cells = row.find_all(['th', 'td'])
            row_data = []
            for cell in cells:
                cell_text = cell.get_text(strip=True).replace('\xa0', ' ')
                cell_text = (cell_text.replace('$', '')
                             .replace('(1)', '').replace('(2)', '').replace('(3)', '')
                             .replace(' (1)', '').replace(' (2)', '').replace(' (3)', ''))
                if cell_text and cell_text != '(' and cell_text != ')':
                    row_data.append(cell_text)
            if row_data:
                table_data.append(row_data)

        df = pd.DataFrame(table_data)
        tables_dict[f"table_{i + 1}"] = df

    # Table 1 - Consolidated Statements of Earnings

    table_1_key = None

    for key, df in tables_dict.items():
        if 'Total investments and cash' in df.values:
            table_1_key = key
            break

    if table_1_key:
        target_table = tables_dict[table_1_key].copy()
        print(target_table)
        target_table = (
            target_table.rename(columns={0: 'Name'}))

        assets_index = target_table[target_table['Name'] == 'Assets:'].index[0]
        target_table_assets = target_table.iloc[assets_index:]

        dates_str = target_table.iloc[:assets_index].to_string(index=False)

        month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                       'November', 'December']
        for month in month_names:
            dates_str = dates_str.replace(month, f'|{month}')

        dates_list = dates_str.split('|')

        dates_list = [date.strip() for date in dates_list if date.strip()]
        dates_list_filtered = [date for date in dates_list if any(month in date for month in month_names)]
        dates_list_filtered = [date.replace('None', '').replace('\n', '') for date in dates_list_filtered]
        dates_list_filtered = [re.sub(r'\s+', ' ', date.replace('(In millions)', '')).strip() for date in
                               dates_list_filtered]

        target_table.columns = ['Name'] + dates_list_filtered

        for col_index in range(1, len(target_table.columns)):
            non_empty_index = target_table[target_table.columns[col_index]].first_valid_index()
            if non_empty_index is not None:
                new_col_name = target_table.iloc[non_empty_index, col_index]
                target_table.rename(columns={target_table.columns[col_index]: new_col_name}, inplace=True)

        target_table = target_table.iloc[1:, ].reset_index(drop=True)

        target_table['Name'] = target_table['Name'].str.replace('-', ' ')
        target_table['Name'] = target_table['Name'].apply(lambda x: x.split('In thousands:')[0].strip())
        target_table['Name'] = target_table['Name'].apply(lambda x: x.split('sale,')[0].strip())
        target_table['Name'] = target_table['Name'].apply(lambda x: x.split(', net')[0].strip())
        target_table['Name'] = target_table['Name'].apply(lambda x: x.split('(includes')[0].strip())
        target_table['Name'] = target_table['Name'].apply(lambda x: x.split('(c')[0].strip())
        target_table['Name'] = target_table['Name'].apply(lambda x: x.split('(a')[0].strip())
        target_table['Name'] = target_table['Name'].apply(lambda x: x.split('(f')[0].strip())

        if not comp_t1.empty:
            target_table.drop_duplicates(subset='Name', inplace=True)
            comp_t1.drop_duplicates(subset='Name', inplace=True)
            comp_t1 = pd.merge(comp_t1, target_table, on='Name', how='outer', suffixes=('', '_new'))
            comp_t1 = comp_t1[[col for col in comp_t1.columns if not col.endswith('_new')]]
        else:
            target_table.drop_duplicates(subset='Name', inplace=True)
            comp_t1.drop_duplicates(subset='Name', inplace=True)
            comp_t1 = target_table.copy()
    else:
        print("No table with 'Total investments and cash' found.")
