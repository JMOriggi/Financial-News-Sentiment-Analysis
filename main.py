import get_news
import get_price
import analysis
import plot
import matplotlib.pyplot as plt
tickers = [['JNJ','MRNA','PFE'],
           ['AAPL','MSFT','GOOG'], #,'FB','NVDA'],
           ['GM','F','TSLA'],
           ['PYPL','MA','JPM'],
           ['NFLX','AMZN','DIS'],
           ['T','VZ']]
title = ['Health','Technology','Automotive','Financial','Media','Communication']

## Init
index = 1 #0-5
tickers = tickers[index]
title = title[index]
load_data = True
flag_save = False

## Load data: from file or web
if load_data:
    df_news_dict_raw = get_news.from_file(tickers)
    df_price_dict = get_price.yfinance(tickers, flag_save = flag_save)
    #df_price_dict = get_price.from_file(tickers)
else: 
    df_news_dict_raw = get_news.finviz(tickers, flag_save = flag_save)
    df_price_dict = get_price.yfinance(tickers, flag_save = flag_save)

## Add additional info to df
df_price_dict = get_price.indicators(df_price_dict)
df_news_dict = analysis.extract_sentiment(df_news_dict_raw)

## Process aggregation of the data: for visualization and correlation
df_agg_dict_vis = analysis.prepare_df_vis(df_price_dict, df_news_dict)
df_agg_dict_corr = analysis.prepare_df_corr(df_price_dict, df_news_dict)

## Plot visualization of the raw data
#plot.dyn_chart(df_agg_dict_vis, tickers, title)

## Analyze Causality and correlation
corr_s_dict = []
corr_p_dict = []
for ticker in tickers:
    print(f'\n --- Correlation and Causality Analysis for {ticker}')
    data1 = []
    data2 = []
    for name in ['price_ratio','mom_ratio','vol_ratio']:
        print(f'\n - name {name}')
        corrP, corrS = analysis.corr(df_agg_dict_corr[ticker], name)
        data1.append(corrP)
        data2.append(corrS)
    corr_s_dict.append(data1)
    corr_p_dict.append(data2)

## Plot correlation bar chart
plot.radar_chart(corr_s_dict, tickers)
plot.radar_chart(corr_p_dict, tickers)