#!pip install yfinance
import pandas as pd
import yfinance as yf
import numpy as np


def save_csv(df, name):
    from datetime import date
    today = date.today()
    df.to_csv(r'data/'+name+'_price_'+str(today)+'.csv', index = True, header=True)#
    print(f'File {name} Saved')

def from_file(tickers):
    df_price_dict = {}
    #col_list = ['datetime', 'headline']
    for ticker in tickers:
        df = pd.read_csv('data/'+ticker+'_price.csv') #, usecols=col_list)
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        df_price_dict[ticker] = df.set_index('Datetime')
    return df_price_dict

def yfinance(tickers, flag_save = False):
    print('PRICE --- Get yfinance data')
    ## GET PRICE DATA 
    df_price_dict = {}
    for ticker in tickers:
        df = yf.download(tickers=ticker, period='7d', interval='1m', group_by= "Ticker")
        # eliminate timezone
        df.index = df.index.tz_localize(None)
        # reindex
        #cur_df = cur_df.asfreq('1Min') # resample Days and fill values
        # save
        df_price_dict[ticker] = df.copy()
        
    # Save
    if flag_save:
        for ticker in tickers:
            save_csv(df_price_dict[ticker], ticker)
        
    return df_price_dict

def indicators(df_price_dict):
    print('PRICE --- Compute price indicators')
    # Indicator methods
    def get_rsi(df, time_window=14):
        diff = df['Adj Close'].copy().diff()
        up_chg = 0 * diff
        down_chg = 0 * diff
        up_chg[diff > 0] = diff[diff>0]
        down_chg[diff < 0] = diff[diff<0]
        up_chg_avg   = up_chg.ewm(com=time_window-1, min_periods=time_window).mean()
        down_chg_avg = down_chg.ewm(com=time_window-1, min_periods=time_window).mean()
        rs = abs(up_chg_avg/down_chg_avg)
        df_rsi = 100 - 100/(1+rs)
        return df_rsi
    def get_vol(df):
        sma_30 = df['Adj Close'].rolling(window=30).mean()
        std_30 = df['Adj Close'].rolling(window=30).std() # set .std(ddof=0) for population std instead of sample
        bb_high = sma_30 + (std_30 * 2)
        bb_low = sma_30 - (std_30 * 2)
        bb = (df['Adj Close'] - bb_low) / (bb_high - bb_low)
        return std_30
    def get_trend(df):
        df['Trend'] = df['Adj Close'].ewm(80).mean()
        return df['Trend']
    
    tickers = df_price_dict.keys()
    for ticker in tickers:
        rsi = get_rsi(df_price_dict[ticker])
        vol = get_vol(df_price_dict[ticker])
        trend = get_trend(df_price_dict[ticker])
        df_price_dict[ticker]['Momentum'] = rsi
        df_price_dict[ticker]['Volatility'] = vol
        df_price_dict[ticker]['Trend'] = trend
    
    return df_price_dict
    
    
