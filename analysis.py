import nltk
'''nltk.download('vader_lexicon')
nltk.download('movie_reviews')
nltk.download('punkt')'''
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np

# for correlation and causality analysis
from numpy import mean
from numpy import std
from numpy import cov
from scipy.stats import pearsonr
from scipy.stats import spearmanr
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.stattools import grangercausalitytests
import matplotlib.pyplot as plt

def extract_sentiment(df_news_dict):
    print('ANALYSIS --- Extract sentiment')
    def extract(x): 
        res = SentimentIntensityAnalyzer().polarity_scores(x)['compound']
        #if ((res > -0.5) and (res < 0.5)):
        #    res = 0
        return res
    df_dict = df_news_dict.copy()
    tickers = df_dict.keys()
    for ticker in tickers:
        df = df_dict[ticker].copy()
        scores = df['headline'].apply(extract)
        scores = pd.DataFrame(scores)
        scores = scores.rename(columns={"headline": "compound"})
        df = df.join(scores.compound) 
        df_dict[ticker] = df.groupby(['datetime'])['compound'].sum() #.mean()
        print(f'Number of {ticker} news: {len(df)}')
        print(f'Number of {ticker} scores: {len(df_dict[ticker])}')
        
    # Visualize
    #mean_scores = df_news_dict[tickers[2]].groupby(['date']).mean() # Group by date and ticker columns from scored_news and calculate the mean
    #mean_scores.plot(kind = 'bar')
    return df_dict


def prepare_df_vis(df_price_dict, df_news_dict):
    print('ANALYSIS --- Aggregate news and price data for visualization')
    ## AGGREGATE DATA: to visualize price and news data at the same time
    df_agg_dict = {}
    tickers = df_news_dict.keys()
    for ticker in tickers:
        # Get current ticker infos: news sentiment and price indicators
        df_price = df_price_dict[ticker]
        df_news = df_news_dict[ticker]
        df_price['datetime'] = df_price.index
        # Aggregate
        df_agg = df_price.reset_index().merge(df_news, how='left', left_on='datetime', right_on='datetime')
        df_agg = df_agg.set_index('Datetime')
        df_agg = df_agg.drop(['datetime'], axis=1)
        # Set sentiment signals
        df_agg['sent_pos'], df_agg['neg_pos'] = np.nan, np.nan
        df_agg['sent_pos'][df_agg.compound > 0] = df_agg.compound[df_agg.compound > 0]
        df_agg['neg_pos'][df_agg.compound < 0] = df_agg.compound[df_agg.compound < 0]
        df_agg['pos_price'], df_agg['neg_price']  = np.nan, np.nan
        df_agg['pos_price'][df_agg.compound > 0] = df_agg.Close[df_agg.compound > 0]
        df_agg['neg_price'][df_agg.compound < 0] = df_agg.Close[df_agg.compound < 0]
        df_agg['pos_mom'], df_agg['neg_mom']  = np.nan, np.nan
        df_agg['pos_mom'][df_agg.compound > 0] = df_agg.Momentum[df_agg.compound > 0]
        df_agg['neg_mom'][df_agg.compound < 0] = df_agg.Momentum[df_agg.compound < 0]
        df_agg['pos_vol'], df_agg['neg_vol']  = np.nan, np.nan
        df_agg['pos_vol'][df_agg.compound > 0] = df_agg.Volatility[df_agg.compound > 0]
        df_agg['neg_vol'][df_agg.compound < 0] = df_agg.Volatility[df_agg.compound < 0]
        df_agg_dict[ticker] = df_agg
    
    # Visualize
    for ticker in tickers:
        num_scores = len(df_news_dict[ticker])
        num_price_scores = len(df_agg_dict[ticker][df_agg_dict[ticker]['compound'].notnull()])
        print(f'Number of {ticker} scores: {num_scores}')
        print(f'Number of {ticker} price scores correspondance: {num_price_scores}')
    
    return df_agg_dict



def prepare_df_corr(df_price_dict, df_news_dict):
    print('ANALYSIS --- Aggregate news and price data for correlation')
    df_agg_dict = {}
    tickers = df_news_dict.keys()
    for ticker in tickers:
        
        # GET DATA FOR CORRELATION: 60min
        df_news = df_news_dict[ticker].resample('60min').sum() #9-10, 11-12, ..., 15-16 
        df_price = df_price_dict[ticker].resample('60min').mean() #9-10, 11-12, ..., 15-16
        df_price['datetime'] = df_price.index
        # Aggregate per hour
        df_final = df_price.reset_index().merge(df_news, how='left', left_on='datetime', right_on='datetime')
        df_final = df_final.set_index('Datetime')
        
        df_scores = []
        prev = [np.nan, np.nan, np.nan]
        for index, row in df_final.iterrows():
            if index.hour >= 9 and index.hour < 17:
                datetime = index
                sentiment = row.compound
                price_before = prev[0]
                price_after = row.Close
                mom_before = prev[1]
                mom_after = row.Momentum
                vol_before = prev[2]
                vol_after = row.Volatility
                if price_after > 0 and price_before > 0:
                    price_ratio = np.log(price_after/price_before)
                else:
                    price_ratio = np.nan
                if mom_after > -10 and mom_before > -10:
                    mom_ratio = np.log(mom_after/mom_before)
                else:
                    mom_ratio = np.nan
                if vol_after > -10 and vol_before > -10:
                    vol_ratio = np.log(vol_after/vol_before)
                else:
                    vol_ratio = np.nan
                df_scores.append([datetime, sentiment, price_ratio, mom_ratio, vol_ratio, price_before, price_after, mom_before, mom_after, vol_before, vol_after])
                if index.hour != 16:
                    prev = [price_after, mom_after, vol_after]
        columns = ['datetime', 'sentiment','price_ratio','mom_ratio','vol_ratio','price_before','price_after', 'mom_before', 'mom_after', 'vol_before', 'vol_after']
        df_agg_dict[ticker] = pd.DataFrame(df_scores, columns=columns)
    
    return df_agg_dict

def corr(df, ratio_name):
    '''Correlation (-1 and 1, 0 no corr (higher than 0.5)):
        - pearsonr coef 
        - spearmanr coef
    Granger to understand if col 1 is cause of the next
    1col is affected by the 2col
    0.05 bigger is worst
    '''
    data_cleaned = df[[ratio_name, 'sentiment']].dropna()
    data1_clean = data_cleaned['sentiment'].to_numpy()
    data2_clean = data_cleaned[ratio_name].to_numpy()
    print(f'Len of sentiment measure: {len(data1_clean)}')
    print(f'Len of sentiment measure: {len(data2_clean)}')
    # The coefficient returns a value between -1 and 1 that represents the limits of correlation 
    # from a full negative correlation to a full positive correlation. 
    # A value of 0 means no correlation. 
    # The value must be interpreted, where often a value below -0.5 or above 0.5 indicates a notable correlation, 
    # and values below those values suggests a less notable correlation.
    # Correlation coefficient is highly sensitive to a few abnormal values (outliers).
    # calculate Pearson's correlation
    corrP, _ = pearsonr(data1_clean, data2_clean)
    print('Pearsons correlation: %.3f' % corrP)
    # Two variables may be related by a nonlinear relationship, such that the relationship is stronger or 
    # weaker across the distribution of the variables.
    # Further, the two variables being considered may have a non-Gaussian distribution.
    # In this case, the Spearman’s correlation coefficient (named for Charles Spearman) 
    # can be used to summarize the strength between the two data samples. 
    # This test of relationship can also be used if there is a linear relationship between the variables, 
    # but will have slightly less power (e.g. may result in lower coefficient scores).
    # calculate spearman's correlation
    corrS, _ = spearmanr(data1_clean, data2_clean)
    print('Spearmans correlation: %.3f' % corrS)
    # Null hypothesis (H0): Xt doesn not granger causes Yt.
    # Alternate hypothesis (H1): Xt granger causes Yt.
    #second column in the data should be the cause of the first column!!!
    # 4 is the number of lags in here
    #grangercausalitytests(data_cleaned, 1, addconst=True, verbose= True)
    ## If the p value is less then 0.05 we reject the null hypothesis with (95% confidence),
    ## which means in our case there IS a granger causality!!!
    return np.abs(corrP), np.abs(corrS)



   
    
