## PLOT DATA
import numpy as np
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode,  plot
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import mplfinance as mpf

def chart(df):
    fig = mpf.figure(figsize=(10, 7)) 
    ax = fig.add_subplot(2,1,1) 
    av = fig.add_subplot(2,1,2, sharex=ax)
    mpf.plot(df, type='candle', ax=ax, volume=av)

def radar_chart(data, tickers):
    #data = [[30, 25, 50],[40, 23, 51],[35, 22, 45]]
    tickers = ['JNJ','MRNA','PFE']
    X = np.arange(3)
    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    ax.bar(X + 0.00, data[0], color = 'b', width = 0.25)
    ax.bar(X + 0.25, data[1], color = 'g', width = 0.25)
    ax.bar(X + 0.50, data[2], color = 'r', width = 0.25)
    colors = {tickers[0]:'red', tickers[1]:'green', tickers[2]:'blue'}         
    labels = list(colors.keys())
    handles = [plt.Rectangle((0,0),1,1, color=colors[label]) for label in labels]
    ax.legend(handles, labels)

def dyn_chart(df_dict, tickers, title):
    if len(tickers) > 2:
        fig = make_subplots(rows=4, cols=len(tickers), shared_xaxes=True, 
                            subplot_titles=(tickers[0], tickers[1], tickers[2]),
                            vertical_spacing=0.01,
                            row_width=[0.2, 0.2, 0.2, 0.7]
                            )
    else:
        fig = make_subplots(rows=4, cols=len(tickers), shared_xaxes=True, 
                            subplot_titles=(tickers[0], tickers[1]),
                            vertical_spacing=0.01,
                            row_width=[0.2, 0.2, 0.2, 0.7]
                            )
    fig.update_layout(title_text=title, xaxis=dict(range=[df_dict[tickers[0]].index[0], df_dict[tickers[0]].index[-1]])) #,width = 1200, height = 600) 
           
    for i, ticker in enumerate(tickers):
        col = i+1
        data = df_dict[ticker]
        print(f'ticker = {ticker}')
        fig.update_xaxes(
            rangebreaks=[
                dict(bounds=["sat", "mon"]), #hide weekends
                dict(bounds=[16, 9], pattern="hour") 
            ]
        )
        '''fig.add_trace(go.Candlestick(x=data.index, yaxis='y1',
                        open=data['Open'],
                        high=data['High'],
                        low=data['Low'],
                        close=data.Close, name = 'market data',visible="legendonly"), row=1,col=col)'''
        # ------------------------- Price
        fig.add_trace(go.Scatter(x=data.index, y=data.Close, name='Price', line=dict(color='royalblue', width=1),showlegend=False), row=1,col=col) #royalblue, firebrick
        fig.add_trace(go.Scatter(x=data.index, y=data.Trend, name='Trend', line=dict(color='firebrick', width=1),showlegend=False), row=1,col=col)
        # ------------------------- Momentum 
        fig.add_trace(go.Scatter(x=data.index, y=data.Momentum, name='Momentum', line=dict(color='royalblue', width=1),showlegend=False), row=2,col=col)
        # ------------------------- Volatility    
        fig.add_trace(go.Scatter(x=data.index, y=data.Volatility, name='Volatility', line=dict(color='royalblue', width=1),showlegend=False),row=3,col=col)
        # ------------------------- Markers 
        fig.add_trace(go.Scatter(x=data.index, y=data.pos_price, mode='markers', name='Sentiment Positive', marker=go.Marker(size=8, symbol='circle-dot', color='green'),showlegend=False),row=1,col=col)
        fig.add_trace(go.Scatter(x=data.index, y=data.neg_price, mode='markers', name='Sentiment Negative', marker=go.Marker(size=8, symbol='circle-dot', color='red'),showlegend=False),row=1,col=col)
        fig.add_trace(go.Scatter(x=data.index, y=data.pos_mom, mode='markers', name='Sentiment Positive', marker=go.Marker(size=8, symbol='circle-dot', color='green'),showlegend=False),row=2,col=col)
        fig.add_trace(go.Scatter(x=data.index, y=data.neg_mom, mode='markers', name='Sentiment Negative', marker=go.Marker(size=8, symbol='circle-dot', color='red'),showlegend=False),row=2,col=col)
        fig.add_trace(go.Scatter(x=data.index, y=data.pos_vol, mode='markers', name='Sentiment Positive', marker=go.Marker(size=8, symbol='circle-dot', color='green'),showlegend=False),row=3,col=col)
        fig.add_trace(go.Scatter(x=data.index, y=data.neg_vol, mode='markers', name='Sentiment Negative', marker=go.Marker(size=8, symbol='circle-dot', color='red'),showlegend=False),row=3,col=col)
        fig.add_trace(go.Bar(x=data.index, y=data.sent_pos, name="Sentiment Positive",marker_color ='green',marker_line_width=1.5, marker_line_color='green', opacity=0.5,showlegend=False),row=4,col=col)
        fig.add_trace(go.Bar(x=data.index, y=data.neg_pos, name="Sentiment Negative",marker_color ='red',marker_line_width=1.5, marker_line_color='red', opacity=0.5,showlegend=False),row=4,col=col)
        # Layout
        if col == 1:
            fig.update_yaxes(title_text="Price", row=1, col=col)
            fig.update_yaxes(title_text="Mom", row=2, col=col)
            fig.update_yaxes(title_text="Vola", row=3, col=col)
            fig.update_yaxes(title_text="Sent", row=4, col=col)
        # Fix axes
        fig.update_layout(xaxis=dict(range=[df_dict[tickers[i]].index[0], df_dict[tickers[i]].index[-1]]))
        fig.update_xaxes(rangeslider_visible=False, rangeselector=dict(visible = True))
        #fig.update_xaxes(row=2, col=col, rangeslider_visible=False, rangeselector_visible=False)
    #Show
    plot(fig)