import requests
import time
import random
import re
from bs4 import BeautifulSoup
import pandas as pd

from functions_data_cleaning import clean_table, find_index, find_index_item, find_index_second

comp_list = pd.read_csv("files/000_desc.csv")
comp_list['CIK'] = comp_list['CIK'].apply(lambda x: str(x).zfill(10))

p1_s = ['part i financial information', 'part i']
p1_e = ['part ii other information', 'pat ii']

t1_s = ['consolidated statements of income', 'consolidated statements of earnings',
        'consolidated statements of operations']
t1_e = ['see accompanying notes to condensed consolidated financial statements (unaudited).',
        'consolidated statements of comprehensive income (loss)',
        'condensed consolidated statements of comprehensive income', 'consolidated balance sheets']
t1_i = ['revenues:', 'revenue']

t2_s = ['condensed consolidated statements of financial position', 'consolidated balance sheets']
t2_e = ['see accompanying notes to condensed consolidated financial statements (unaudited).',
        'condensed consolidated statements of shareholders’ equity (deficit)', 'consolidated statements of cash flows']
t2_i = ['assets:', 'assets']

t3_s = ['condensed consolidated statements of cash flows', 'consolidated statements of cash flows']
t3_e = ['see accompanying notes to condensed consolidated financial statements (unaudited).',
        'notes to the consolidated financial statements (unaudited)     ']
t3_i = ['cash flows from operating activities', 'cash flows from operating activities:']

for cik in comp_list['CIK']:

    comp_name = comp_list.loc[comp_list['CIK'] == cik, 'Company name'].values[0]
    comp_ticker = comp_list.loc[comp_list['CIK'] == cik, 'Ticker'].values[0]

    path_filings = str('files/Data/Financials/' + comp_ticker + '_filings.csv')
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

        # Scrap data
        soup = BeautifulSoup(response.text, "html.parser")
        hop = [span.get_text().lower() for span in soup.find_all('span')]

        if not hop:  # files of old format
            hop_old = [span.get_text().lower() for span in soup.find_all(['td', 'b'])]

            hop = []
            for item in hop_old:
                hop.extend(item.split('         '))

        hop = [s.strip().replace('\xa0', ' ')
               for s in hop if s.strip() and s.strip() != '\xa0' and s.strip() not in ['$', '', '\n', '—']]
        hop = [s.strip().replace('i.', 'i') for s in hop]

        # Extract quarter
        date_to_extract = ' '.join(hop[0:50]).lower()
        q_to_extract = ''

        if 'ended march' in date_to_extract:
            q_to_extract = 'Q1'
        elif 'ended june' in date_to_extract:
            q_to_extract = 'Q2'
        elif 'ended september' in date_to_extract:
            q_to_extract = 'Q3'
        elif 'ended december' in date_to_extract:
            q_to_extract = 'Q4'

        years_extracted = re.findall(r'\b\d{4}\b', date_to_extract)
        year_to_extract = ''
        for year in years_extracted:
            year_int = int(year)
            if 1994 <= year_int <= 2024:
                year_to_extract = year_int
                break

        col_name = str(q_to_extract) + '-' + str(year_to_extract)

        # Part 1: Financial Information
        p1_se = find_index(hop, p1_s, p1_e)
        part_1_financial_info = hop[p1_se[0]:p1_se[1]]

        # Table 1: Consolidated Statements of Earnings
        t1_se = find_index_second(part_1_financial_info, t1_s, t1_e)
        table_1 = part_1_financial_info[t1_se[0]:t1_se[-1]]

        t1_ii = find_index_item(table_1, t1_i)
        table_1 = table_1[t1_ii:]

        comp_t1_f = clean_table(table_1, col_name)
        comp_t1 = pd.concat((comp_t1, comp_t1_f))
        print(comp_t1_f)
        print(comp_ticker, filing, url)

        path_table1 = str('files/Data/Financials/' + comp_ticker + '_t1.csv')
        comp_t1.to_csv(path_table1, index=False)

        # Table 2: Consolidated Balance Sheets
        t2_se = find_index_second(part_1_financial_info, t2_s, t2_e)
        table_1 = part_1_financial_info[t2_se[0]:t2_se[1]]

        t2_ii = find_index_item(table_1, t2_i)
        table_1 = table_1[t2_ii:]

        comp_t2_f = clean_table(table_1, col_name)
        comp_t2 = pd.concat((comp_t2, comp_t2_f))
        print(comp_t2_f)
        print(comp_ticker, filing, url)

        path_table2 = str('files/Data/Financials/' + comp_ticker + '_t2.csv')
        comp_t2.to_csv(path_table2, index=False)

        # Table 3: Consolidated Balance Sheets
        t3_se = find_index(part_1_financial_info, t3_s, t3_e)
        table_1 = part_1_financial_info[t3_se[0]:t3_se[1]]

        t3_ii = find_index_item(table_1, t3_i)
        table_1 = table_1[t3_ii:]

        comp_t3_f = clean_table(table_1, col_name)
        comp_t3 = pd.concat((comp_t3, comp_t3_f))
        print(comp_t3_f)
        print(comp_ticker, filing, url)

        path_table3 = str('files/Data/Financials/' + comp_ticker + '_t3.csv')
        comp_t3.to_csv(path_table3, index=False)
