import pandas as pd
import re


def clean_table (separated_table, column_name):
    text_data = [s.strip().replace('\xa0', ' ') for s in separated_table if
                 s.strip() and s.strip() != '\xa0' and s.strip() not in ['$', '(1)']]
    text_data = [s.strip().replace('(1)', '') for s in text_data]
    text_data = [s.strip().replace('(', '-') for s in text_data]
    text_data = [s.strip().replace(')', '') for s in text_data]
    text_data = [s.strip().replace(',', '') for s in text_data]

    text_data_float = []
    for s in text_data:
        if s.replace('.', '', 1).replace('-', '', 1).isdigit():  # Check if the string is a numeric entry
            text_data_float.append(float(s.replace(',', '')))  # Convert to float and remove commas
        else:
            text_data_float.append(s)

    data = []
    cat_value = ''

    for i, value in enumerate(text_data_float):
        if isinstance(value, str):
            if i + 1 < len(text_data_float):
                if isinstance(text_data_float[i + 1], str):
                    cat_value = value
                else:
                    new_value = cat_value + " " + value
                    data.append([new_value, text_data_float[i + 1]])

    data = pd.DataFrame(data, columns=['Name', column_name])
    data = data[0:-1]

    return data


def transform_string(text):
    text = re.sub(r'[^\w\s]', '', text)
    text = text.lower()
    text = text.replace(' ', '_')
    return text