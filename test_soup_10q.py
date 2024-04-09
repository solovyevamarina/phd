import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

from functions_data_cleaning import clean_table


url_q3 = "https://www.sec.gov/Archives/edgar/data/4977/000000497723000177/afl-20230930.htm"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
}

response = requests.get(url_q3, headers=headers)

# Scrap data
soup = BeautifulSoup(response.text, "html.parser")
hop = [span.get_text() for span in soup.find_all('span')]

# Extract quarter
cover = hop[hop.index('Quarterly Report on Form 10-Q'):hop.index('Table of Contents')]
date_to_extract = str(cover[1]).replace('\xa030', '')
year_to_extract = date_to_extract[-5:].replace(' ', '')
q_to_extract = []

if 'March' in date_to_extract:
    q_to_extract = 'Q1'
elif 'June' in date_to_extract:
    q_to_extract = 'Q2'
elif 'September' in date_to_extract:
    q_to_extract = 'Q3'
elif 'December' in date_to_extract:
    q_to_extract = 'Q4'

col_name = q_to_extract + '-' + year_to_extract


# Part 1: Financial Information
part_1_financial_info = hop[hop.index('PART I. FINANCIAL INFORMATION'):hop.index('PART II. OTHER INFORMATION')]


# Table 1: Consolidated Statements of Earnings
table_1 = part_1_financial_info[
          part_1_financial_info.index('Consolidated Statements of Earnings'):
          part_1_financial_info.index('Consolidated Statements of Comprehensive Income (Loss)')]

table_1 = table_1[table_1.index('Revenues:'):]

AFL_t1 = clean_table(table_1, col_name)
print(AFL_t1)


# Table 2: Consolidated Statements of Comprehensive Income (Loss)
table_2 = part_1_financial_info[
          part_1_financial_info.index('Consolidated Statements of Comprehensive Income (Loss)'):
          part_1_financial_info.index('Consolidated Balance Sheets')]

table_2 = table_2[table_2.index('Net earnings'):]

AFL_t2 = clean_table(table_2, col_name)
print(AFL_t2)


# Table 3: Consolidated Balance Sheets
table_3 = part_1_financial_info[
          part_1_financial_info.index('Consolidated Balance Sheets'):
          part_1_financial_info.index('Consolidated Statements of Shareholders’ Equity')]

table_3 = table_3[table_3.index('Assets:'):]

AFL_t3 = clean_table(table_3, col_name)
print(AFL_t3)



