
# coding: utf-8

# In[13]:

import pandas as pd
import numpy as np
import glob
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import re


# In[14]:

def adjust_mean(timeseries):
    n=len(timeseries)
    decay=0.99
    weights=np.ones(n)/float(n)
    line=np.array([1.0001**(-decay*(n-t)) for t in np.linspace(1,n,num=n)])
    adjust_weight=line*weights
    return np.sum(adjust_weight*timeseries)


# In[15]:

def read_values(data_list):
    allFiles = glob.glob( "*.csv")
    for name in allFiles:
        data_list[name[:-4]]=pd.read_csv(name)

# In[16]:

def sharp_ratio(df,adjust=False):
    vals=df['value'].values
    hourly_return=np.log(vals[1:]/vals[0:-1])
    if adjust==False:
        volatility=np.std(hourly_return)
        mean=np.mean(hourly_return)
    else:
        mean=adjust_mean(hourly_return)
        volatility=np.power(adjust_mean(np.square(np.array(hourly_return-mean))),0.5)
    return mean/volatility*240.0/np.sqrt(240.0)
        
    


# In[17]:

def volatility(df):
    vals=df['value'].values
    return np.std(vals)


# In[18]:

# def on_off_days(name):
    # p1=	(r'_.*?_')
    # pattern=re.compile(p1)
    # match=re.search(pattern,name).group(0)
    # on=int(re.findall('\d+', match)[0])
    # p2=(r'0_.*')
    # pattern=re.compile(p2)
    # match=re.search(pattern,name).group(0)
    # if match[-2:]=='_0':
	    # off=0
    # else:
	    # off=int(match[-2:])
    # return on,off


# In[19]:

def max_drawdown(df,adjust=False):
    """

    :type adjust: object
    """
    vals=df['value'].values
    n=len(vals)
    print n
    i = np.argmax(np.maximum.accumulate(vals) - vals)
    j = np.argmax(vals[:i])
    decay=0.99
    date_end=df.iloc[i].index.values
    date_start=df.iloc[j].index.values
    if not adjust:
        return ((float(vals[i]) / vals[j]) - 1), date_start, date_end
    else:
        return ((float(vals[i]) / vals[j]) - 1)*1.0001**(-decay*(n-(i+j)/2)), date_start, date_end


# In[20]:

def mins_trading(df):
	return len(df.index.values)*15
	

# In[21]:

def prob_up(df):
    vals=df['value'].values
    hourly_return=np.log(vals[1:]/vals[0:-1])
    temp1=[x>0 for x in hourly_return]
    temp2=[x<0 for x in hourly_return]
    return np.sum(temp1)/float(np.sum(temp1)+np.sum(temp2))


# In[22]:

def cumulate_return(df):
    vals=df['value'].values
    return (vals[-1]/vals[0]-1)


# In[23]:

def ret_drawdown(df):
    vals=df['value'].values
    mean_ret=(vals[-1]/vals[0]-1)/len(vals)
    return -mean_ret/max_drawdown(df)[0]


# In[24]:

def basic_analysis(data_list):
    value_return={}
    for name,data in data_list.iteritems():
	print name
        value_return[name]=(sharp_ratio(data),sharp_ratio(data,True),-max_drawdown(data)[0],-max_drawdown(data,True)[0],
                            prob_up(data),cumulate_return(data),ret_drawdown(data),mins_trading(data),volatility(data))
    return value_return


# In[25]:

if __name__ == '__main__':
    data_list={} #all dataframes
    read_values(data_list)
    performance=basic_analysis(data_list)
    sort_sharp=sorted(performance.items(),key=lambda x: x[1][0] ,reverse=True)
    sort_adjust_sharp=sorted(performance.items(),key=lambda x: x[1][1] ,reverse=True)
    sort_drawdown=sorted(performance.items(),key=lambda x: x[1][2])
    sort_adjust_drawdown=sorted(performance.items(),key=lambda x: x[1][3])
    sort_prob_up=sorted(performance.items(),key=lambda x: x[1][4],reverse=True)
    sort_return=sorted(performance.items(),key=lambda x: x[1][5],reverse=True)
    sort_ret_drawdown=sorted(performance.items(),key=lambda x: x[1][6],reverse=True)

    analysis_df=pd.DataFrame.from_dict(performance,orient='index')
    analysis_df.columns=['sharp','adjusted_sharp','max_drawdown','adjust_drawdown',
                         'prob_up','cumulate_return','ret_drawdown','hours_trading','volatility']
    analysis_df.to_csv('./analysis.csv')


# In[ ]:




# In[ ]:



