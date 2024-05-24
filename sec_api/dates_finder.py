import pandas as pd
import re


def identify_dates(target_table):

    dates_str = (target_table.iloc[:10].to_string(index=False).replace(' ', '').replace('None', '').replace('\n', '')
                 .replace('(Inmillions)', '').replace('(Unaudited)', '').replace('(Inmillions,exceptforshareandper-shareamounts)', ''))

    date_pattern = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\d{1,2},\d{4}'
    dates_list = re.findall(date_pattern, dates_str)

    month_to_quarter = {
        'January': 'Q1', 'February': 'Q1', 'March': 'Q1',
        'April': 'Q2', 'May': 'Q2', 'June': 'Q2',
        'July': 'Q3', 'August': 'Q3', 'September': 'Q3',
        'October': 'Q4', 'November': 'Q4', 'December': 'Q4'
    }

    # Function to convert date to quarter format
    def convert_to_quarter(date):
        month_day, year = date.split(',')
        quarter = month_to_quarter[month_day[:-2]]
        return f"{quarter}_{year}"

    quarter_dates = [convert_to_quarter(date) for date in dates_list]

    return quarter_dates[0:2]


def identify_dates_soup(tables_dict):
    table_1_key = None

    for key, df in tables_dict.items():
        if 'Total assets' in df.values:
            table_1_key = key
            break

    dates_str = tables_dict[table_1_key].to_string(index=False).replace(' ', '')

    date_pattern = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\d{1,2},\d{4}'
    dates_list = list(set(re.findall(date_pattern, dates_str)))

    month_to_quarter = {
        'January': 'Q1', 'February': 'Q1', 'March': 'Q1',
        'April': 'Q2', 'May': 'Q2', 'June': 'Q2',
        'July': 'Q3', 'August': 'Q3', 'September': 'Q3',
        'October': 'Q4', 'November': 'Q4', 'December': 'Q4'
    }

    # Function to convert date to quarter format
    def convert_to_quarter(date):
        month_day, year = date.split(',')
        quarter = month_to_quarter[month_day[:-2]]
        return f"{quarter}_{year}"

    quarter_dates = [convert_to_quarter(date) for date in dates_list]

    return list((quarter_dates[1], quarter_dates[0]))
