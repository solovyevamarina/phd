import pandas as pd
import re
from sec_api.dates_finder import identify_dates_soup

#
# table_key = 'Total assets'
# name_key = 'Assets:'
#
# table_key = 'Total liabilities'
# name_key = 'Liabilities:'


def total_cleaner(tables_dict, table_key, name_key):
    table_1_key = None

    for key, df in tables_dict.items():
        if table_key in df.values:
            table_1_key = key
            break

    if table_1_key:
        target_table = tables_dict[table_1_key].copy()
        target_table = (target_table.rename(columns={0: 'Name'}))

        assets_index = target_table[target_table['Name'] == name_key].index[0]
        target_table = target_table.iloc[assets_index:]

        if len(target_table.columns) > 3:
            for col in target_table.columns[1:]:
                none_percentage = (target_table[col].eq('None') | target_table[col].isna()).mean()
                if none_percentage >= 0.8:
                    col_index = target_table.columns.get_loc(col)
                    prev_col_index = col_index - 1
                    for idx, val in target_table.iloc[:, prev_col_index].items():
                        if pd.notnull(val):
                            target_table.at[idx, prev_col_index] = val
                            target_table.at[idx, col] = None
        target_table = target_table[target_table.columns[0:3]]
        target_table.columns = ['Name', 0, 1]

        def clean_name(name):
            name = name.replace('-', ' ')
            name = name.replace('.10par', '.10 par')
            name = re.sub(r'\([^()]*\)(?!\s*losses)', '', name)
            separators = ['In thousands:', 'sale,', ', net', '(includes', '(c', '(a', '(f']
            for separator in separators:
                name = name.split(separator)[0].strip()
            return name

        target_table['Name'] = target_table['Name'].apply(clean_name)
        mask = ~(target_table['Name'].str.isdigit() | (target_table['Name'] == '(Unaudited)'))
        target_table = target_table[mask]

        return target_table


def htm_cleaner(soup):
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
                cell_text = (cell_text.replace('$', ''))
                if cell_text and cell_text != '(' and cell_text != ')':
                    row_data.append(cell_text)
            if row_data:
                table_data.append(row_data)

        df = pd.DataFrame(table_data)
        tables_dict[f"table_{i + 1}"] = df

    target_table = total_cleaner(tables_dict, 'Total assets', 'Assets:')
    dates = identify_dates_soup(tables_dict)
    target_table.columns = ['Name'] + dates

    if 'Total liabilities' in target_table.values:
        target_table = total_cleaner(tables_dict, 'Total assets', 'Assets:')
        dates = identify_dates_soup(tables_dict)
        target_table.columns = ['Name'] + dates
    else:
        target_table_a = total_cleaner(tables_dict, 'Total assets', 'Assets:')
        target_table_l = total_cleaner(tables_dict, 'Total liabilities', 'Liabilities:')
        target_table = pd.concat(((target_table_a, target_table_l)), axis=0)
        target_table.columns = ['Name'] + dates

    return target_table
