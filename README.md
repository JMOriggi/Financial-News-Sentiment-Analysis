# Financial-News-Sentiment-Analysis

Dynamic and interactive html GUI to explore raw data from price indicators and news sentiment.

## News
Extract from parsing finviz news page for a specific list of tickers.
The data is then reorganized, datetime format modified and aggregated.
We apply a Vader sentiment analyzer to the data to extract the sentiment of each news headline.

## Price
We download the data with minute precision from yfinance library.
We extract 3 indicators from the price over 30 timestep:
- Momentum RSI
- Volatility standard deviation
- Exponential moving average

## Visualization & Analysis
We allow a tool for the data exploration of both the sentiment and price information.
This provide some inside that can benefit some traiding strategies as the sentiment work as a confirmation of the trend strenght.
From our analysis there is no clear causality and by consequence the sentiment cannot be used in this setup to predict future trend change of the price.

![Alt text](/git-docs/gui.JPG ) 
