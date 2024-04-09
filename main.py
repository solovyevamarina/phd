import pandas as pd
import yfinance as yf

start_ymd = pd.Timestamp('2000-01-01').strftime('%Y-%m-%d')
end_ymd = pd.Timestamp('2024-04-01').strftime('%Y-%m-%d')

list_of_companies_in_financials = ['AFL', 'ALL', 'AXP', 'AIG', 'AMP', 'AON', 'ACGL', 'AJG', 'AIZ', 'BAC', 'BK', 'BRK.B',
                                   'BLK', 'BX', 'BRO', 'COF', 'CBOE', 'SCHW', 'CB', 'CINF', 'C', 'CFG', 'CME', 'CMA',
                                   'CPAY', 'DFS', 'EG', 'FDS', 'FIS', 'FITB', 'FI', 'BEN', 'GPN', 'GL', 'GS', 'HIG',
                                   'HBAN', 'ICE', 'IVZ', 'JKHY', 'JPM', 'KEY', 'L', 'MTB', 'MKTX', 'MMC', 'MA', 'MET',
                                   'MCO', 'MS', 'MSCI', 'NDAQ', 'NTRS', 'PYPL', 'PNC', 'PFG', 'PGR', 'PRU', 'RJF', 'RF',
                                   'SPGI', 'STT', 'SYF', 'TROW', 'TRV', 'TFC', 'USB', 'V', 'WRB', 'WFC', 'WTW']

for c in list_of_companies_in_financials:
    df_yf_h = yf.Ticker(c).history(start=start_ymd, end=end_ymd)
    fin_path = 'C:/Users/Marina/Documents/PhD/Data/Financials/' + c + '_history.csv'
    df_yf_h.to_csv(fin_path)
    print(c)

