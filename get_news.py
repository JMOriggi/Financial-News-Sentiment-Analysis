from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import os
import pandas as pd
import matplotlib.pyplot as plt

def save_csv(df, name):
    from datetime import date
    today = date.today()
    df.to_csv(r'data/'+name+'_news_'+str(today)+'.csv', index = True, header=True)#
    print(f'File {name} Saved')

def from_file(tickers):
    df_news_dict = {}
    col_list = ['datetime', 'headline']
    for ticker in tickers:
        df = pd.read_csv('data/'+ticker+'_news.csv', usecols=col_list)
        df.datetime = pd.to_datetime(df.datetime)
        df_news_dict[ticker] = df
    return df_news_dict

def finviz(tickers, flag_save = False):
    print('NEWS --- Get finviz news')
    ## GET DATA: Date, Time and News Headlines Data
    finwiz_url = 'https://finviz.com/quote.ashx?t=' #'https://finviz.com/crypto_charts.ashx?t=BTCUSD'
    
    news_tables = {}
    for ticker in tickers:
        print(f'Processing {ticker}')
        url = finwiz_url + ticker
        req = Request(url=url, headers={'user-agent': 'my-app/0.0.1'}) 
        response = urlopen(req)  
        html = BeautifulSoup(response,"html.parser") # Read the contents of the file into 'html'
        news_table = html.find(id='news-table') # Find 'news-table' in the Soup and load it into 'news_table'
        news_tables[ticker] = news_table # Dict of bs4.element.Tag with the whole html code (value of the dict) for each ticker (key of the dict)
          
    
    ## PARSE DATA
    # Time conversion method: convert from am pm
    def timeConversion(s):
        if s[-2:] == "AM" :
            if s[:2] == '12':
                a = str('00' + s[2:5] + ':00')
            else:
                a = s[:-2]
        else:
            if s[:2] == '12':
                a = s[:-2]
            else:
                a = str(int(s[:2]) + 12) + s[2:5]  + ':00'
        return a
    # Init
    news_dict = {}
    for ticker in tickers:
        news_dict[ticker] = []
    # Parse   
    for file_name, news_table in news_tables.items(): # Iterate through the news
        for x in news_table.findAll('tr'): # Iterate through all tr tags in 'news_table'
            text = x.a.get_text() 
            date_scrape = x.td.text.split()
            if len(date_scrape) == 1:
                time = date_scrape[0]    
            else:
                date = date_scrape[0]
                time = date_scrape[1]
            ticker = file_name.split('_')[0] # Extract the ticker from the file name, get the string up to the 1st '_' 
            ## readapt datetime
            original_date = date
            original_time = time
            time = timeConversion(time)
            # aggregate per business hour of stock market
            if (int(time[:2]) > 16) or (int(time[:2]) < 10):
                if (int(time[:2]) > 16):
                    time = '09:31:00'
                    if len(date_scrape) != 1:
                        date = date[:4] + str(int(date[4:6])+1) + date[6:]
                elif (int(time[:2]) < 10):
                    time = '09:31:00'
            datetime = date + ' ' + time
            news_dict[ticker].append([datetime, text]) #date, original_date, original_time])
    
    ## DICT TO DF
    columns = ['datetime', 'headline'] #, 'original_date', 'original_time']
    df_news_dict = {}
    for ticker in tickers:
        print(f'Processing again {ticker}')
        df = pd.DataFrame(news_dict[ticker], columns=columns)
        df.datetime = pd.to_datetime(df.datetime)
        df = df.sort_values('datetime') 
        #df.date = pd.to_datetime(df.date).dt.date
        #df.index = df.datetime
        #df = df.drop(['datetime'], axis=1)
        df_news_dict[ticker] = df
    
    # Save
    if flag_save:
        for ticker in tickers:
            save_csv(df_news_dict[ticker], ticker)
    
    return df_news_dict