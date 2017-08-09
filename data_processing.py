import pandas as pd
import numpy as np
from dbWrapper import dbWrapper
from datetime import datetime
from dateutil.relativedelta import relativedelta
import signal_calculator as sc
import matplotlib.pyplot as plt

#commodity set for special formatting
special_set = ['MA', 'OI', 'TA', 'ZC','CF', 'RM','FG','SR']

def main_contract(date,contract):
    date_str=()
    if date.month in range(1,5):
        date_str = (str(date.year)[3]+'05',str(date.year)[3]+'09') if contract in special_set else (str(date.year)[-2:]+'05',str(date.year)[-2:]+'09')
    if date.month in range(5,9):
        date_str = (str(date.year)[3]+'09',str(date.year+1)[3]+'01') if contract in special_set else (str(date.year)[-2:]+'09',str(date.year+1)[-2:]+'01')
    if date.month in range(9,13):
        date_str = (str(date.year+1)[3]+'01',str(date.year+1)[3]+'05') if contract in special_set else (str(date.year+1)[-2:]+'01',str(date.year+1)[-2:]+'05')
    return contract+date_str[0],contract+date_str[1]

def ry_contract(temp_date,contract):
    date=datetime.strptime(temp_date,'%Y%m%d')
    if date.month in range(1,5):
        date_str = (str(date.year)[3]+'05',str(date.year)[3]+'09',str(date.year+1)[3]+'01') if contract in special_set else (str(date.year)[-2:]+'05',str(date.year)[-2:]+'09',str(date.year+1)[-2:]+'01')
    if date.month in range(5,9):
        date_str = (str(date.year)[3]+'09',str(date.year+1)[3]+'01',str(date.year+1)[3]+'05') if contract in special_set else (str(date.year)[-2:]+'09',str(date.year+1)[-2:]+'01',str(date.year+1)[-2:]+'05')
    if date.month in range(9,13):
        date_str = (str(date.year+1)[3]+'01',str(date.year+1)[3]+'05',str(date.year+1)[3]+'09') if contract in special_set else (str(date.year+1)[-2:]+'01',str(date.year+1)[-2:]+'05',str(date.year+1)[-2:]+'09')
    return contract+date_str[0],contract+date_str[1],contract+date_str[2]

def to_string(date):
    if len(str(date.month)) == 1 and len(str(date.day)) == 1:
        return str(date.year) + '0' + str(date.month) + '0' + str(date.day)
    elif len(str(date.month)) == 1 and len(str(date.day)) != 1:
        return str(date.year) + '0' + str(date.month) + str(date.day)
    else:
        return str(date.year) + str(date.month) + str(date.day)

def get_date(contract, start_date, end_date):
    # get the contract dates for a specific contract
    months = ['01', '05', '09']
    start_year = start_date[2:4]
    start_month = start_date[4:6]
    if int(start_month) in range(1, 5):
        start_month = '05'
    elif int(start_month) in range(5, 9):
        start_month = '09'
    elif int(start_month) in range(9, 13):
        start_year = str(int(start_year) + 1)
        start_month = '01'

    end_year = end_date[2:4]
    end_month = end_date[4:6]
    if int(end_month) in range(1, 5):
        end_month = '05'
    elif int(end_month) in range(5, 9):
        end_month = '09'
    elif int(end_month) in range(9, 13):
        end_year = str(int(end_year) + 1)
        end_month = '01'

    contract_date = []
    for year in range(int(start_year), int(end_year) + 1):
        for month in months:
            contract_date.append(str(year) + month)
    contract_date = [x for x in contract_date if int(start_year + start_month) <= int(x) <= int(end_year + end_month)]

    opponent_month = []
    for date in contract_date:
        if date[2:] == '01':
            opponent_month.append(date[0:2] + '05')
        if date[2:] == '05':
            opponent_month.append(date[0:2] + '09')
        if date[2:] == '09':
            opponent_month.append(str(int(date[0:2]) + 1) + '01')
    contract_date = sorted(list(set(opponent_month + contract_date)))
    if contract in special_set:
        contract_date = [x[1:] for x in contract_date]
    return contract_date

def get_ry_date(contract, start_date, end_date):
    # get the contract dates for a specific contract
    months = ['01', '05', '09']
    start_year = start_date[2:4]
    start_month = start_date[4:6]
    if int(start_month) in range(1, 5):
        start_month = '05'
    elif int(start_month) in range(5, 9):
        start_month = '09'
    elif int(start_month) in range(9, 13):
        start_year = str(int(start_year) + 1)
        start_month = '01'

    end_year = end_date[2:4]
    end_month = end_date[4:6]
    if int(end_month) in range(1, 5):
        end_month = '01'
        end_year = str(int(end_year) + 1)
    elif int(end_month) in range(5, 9):
        end_month = '05'
        end_year = str(int(end_year) + 1)
    elif int(end_month) in range(9, 13):
        end_year = str(int(end_year) + 1)
        end_month = '09'

    contract_date = []
    for year in range(int(start_year), int(end_year) + 1):
        for month in months:
            contract_date.append(str(year) + month)
    contract_date = [x for x in contract_date if int(start_year + start_month) <= int(x) <= int(end_year + end_month)]

    return contract_date






def get_price(contract, start_date, end_date,freq='15 Min'):
    # this function get timeseries with specified expiration date
    if freq=='15 Min':
        start_date=datetime(int(start_date[:4]),int(start_date[4:6]),int(start_date[6:8]))-relativedelta(days=40)
        start_date=datetime.strftime(start_date,'%Y%m%d')
    dd = dbWrapper('192.168.10.188')
    cont_name = contract[:-3] if contract[:2] in special_set else contract[:-4]
    spot_price = dd.getSpotPrice(cont_name, start_date, end_date)
    prices = pd.DataFrame()
    if contract[0:2] == 'MA' and datetime.strptime(start_date, '%Y%m%d') <= datetime(2015, 5, 15):
        if int(contract[2:]) < 509:
            try:
                if freq=='15 Min':
                    price_night1 = dd.getNightBars('ME' + contract[2:], start_date, end_date, freq)
                else:
                    price_night1=pd.DataFrame()
            except:
                return prices
            price_day1 = dd.getBars('ME' + contract[2:], start_date, end_date, freq)
        else:
            try:
                if freq == '15 Min':
                    price_night1 = dd.getNightBars(contract, start_date, end_date, freq)
                else:
                    price_night1=pd.DataFrame()
            except:
                return prices
            price_day1 = dd.getBars(contract, start_date, end_date, freq)
        if not price_day1.empty:
            price_day1 = price_day1
        if not price_night1.empty:
            price_night1 = price_night1
        prices = pd.concat([price_night1, price_day1]).sort_values(by=['tradingday', 'bartime'], ascending=[True, True])
    else:
        try:
            if freq == '15 Min':
                price_night = dd.getNightBars(contract, start_date, end_date, freq)
            else:
                price_night=pd.DataFrame()
            price_day = dd.getBars(contract, start_date, end_date, freq)
        except:
            return pd.DataFrame()
        if not price_day.empty:
            price_day = price_day
        if not price_night.empty:
            price_night = price_night
        try:
            prices = pd.concat([price_night, price_day]).sort_values(by=['tradingday', 'bartime'], ascending=[True, True])
        except:
            return pd.DataFrame()
    if freq=='15 Min':
        time_list = []
        for index, row in prices.iterrows():
            date = row['tradingday']
            time = row['bartime']
            moment = datetime(year=int(date[:4]), month=int(date[4:6]), day=int(date[6:8]), hour=int(time[0:2]),
                              minute=int(time[3:5]))
            time_list.append(moment)
        prices['time_list'] = time_list
        prices = prices.set_index(pd.DatetimeIndex(prices['time_list']))
        return prices
    else:
        spot_price_series=pd.Series([0]).append(spot_price['spotprice'])
        spot_price_date = spot_price['tradingday'].append(pd.Series([0]))
        spot_price=pd.DataFrame(dict(tradingday=spot_price_date.values,spotprice=spot_price_series.values))
        spot_price.set_index(spot_price['tradingday'].values,inplace=True)
        prices.set_index(prices['tradingday'].values,inplace=True)
        prices=pd.concat([prices['closeprice'],prices['openinterest'],spot_price['spotprice']],axis=1,join='inner')
        # print prices
        days_left=[]
        for index,row in prices[1:].iterrows():
            today=datetime.strptime(index,'%Y%m%d')
            time_str='1'+contract[-3:] if cont_name in special_set else contract[-4:]
            expiration=datetime.strptime(time_str,'%y%m')
            days_left.append((expiration-today).days)
        prices=prices[1:]
        prices['daysleft']=days_left
        prices['maxposition']=prices['openinterest'].cummax()
        return prices[1:]

def price_concat(contract, start_date, end_date,freq='15 Min'):
    # function to concat same commodity with different expiration dates
    dates = get_ry_date(contract, start_date, end_date)
    price_data = {}
    for date in dates:
        name = contract + date[1:] if contract in special_set else contract+date
        price_data[name] = get_price(name, start_date, end_date, freq)
    # for name, item in price_data.iteritems():
    #     print name
    start_ = datetime.strptime(start_date, '%Y%m%d')
    end_ = datetime.strptime(end_date, '%Y%m%d')
    date_sum = []
    for name, data in price_data.iteritems():
        for index, row in data.iterrows():
            date_sum.append(index)
    all_date = sorted(set(date_sum))
    if freq=='15 Min':
        for date in all_date:
            if date.hour == 15 and date.minute > 0:
                all_date.remove(date)
        date_price_pair = []
        for date in all_date:
            name1,name2=main_contract(date,contract)
            try:
                df1 = price_data[name1]
                price1 = df1.loc[date]['closeprice']
                volume1= df1.loc[date]['volume']
                openint1=df1.loc[date]['openinterest']
                df2 = price_data[name2]
                price2 = df2.loc[date]['closeprice']
                volume2 = df2.loc[date]['volume']
                openint2 = df2.loc[date]['openinterest']
                sp_price = float(price1 - price2)
                date_price_pair.append((date, price1, price2, sp_price,volume1,volume2, openint1, openint2))
            except:
                pass
        return price_data,date_price_pair
    else:
        ry=[]
        for date in all_date:
            name1,name2,name3=ry_contract(date,contract)
            df1,df2,df3=(price_data[name1],price_data[name2],price_data[name3])
            try:
                price1=df1.loc[date]['closeprice']
                spot_price1=df1.loc[date]['spotprice']
                d_left1=df1.loc[date]['daysleft']
                openint1=df1.loc[date]['openinterest']
                ry1=(price1-spot_price1)/d_left1
                price2 = df2.loc[date]['closeprice']
                spot_price2 = df2.loc[date]['spotprice']
                d_left2 = df2.loc[date]['daysleft']
                openint2 = df2.loc[date]['openinterest']
                ry2 = (price2 - spot_price2) / d_left2
                price3 = df3.loc[date]['closeprice']
                spot_price3 = df3.loc[date]['spotprice']
                d_left3 = df3.loc[date]['daysleft']
                openint3 = df3.loc[date]['openinterest']
                ry3 = (price3 - spot_price3) / d_left3
                ry.append((date, price1, price2, price3, spot_price1, spot_price2, spot_price3, d_left1, d_left2,
                           d_left3, ry1, ry2, ry3, openint1,openint2, openint3,
                           df1.loc[date]['maxposition'],df1.loc[date]['maxposition'],df1.loc[date]['maxposition']))
            except:
                pass
        return ry

def value(principal,prices1,prices2,signals):
    #function to calculate values for two leg strategy
    prices=np.diff(np.array([prices1,prices2]),axis=0)[0]
    n=len(prices)
    amount=np.zeros(n)
    pl=np.zeros(n)
    amount[0]=principal/prices[0]*(1 if signals[0]>0 else -1) if signals[0]==2 else 0
    amount_open=0
    for i in range(1,n):
        n_trade=0
        if abs(signals[i])==2:
            p=max(prices1[i],prices2[i])
            amount_open=principal/p if signals[i]>0 else -principal/p
            amount[i] = amount_open+amount[i-1]
        elif abs(signals[i])<2 and signals[i]!=0:
            amount[i]=0
        elif signals[i]==3:
            amount[i]=amount_open-(amount_open/4.0)
            amount_open=amount[i]
        else:
            amount[i]=amount[i-1]
    value=np.zeros(n)
    value[0]=principal
    for i in range(1, n):
        pl[i]=-amount[i-1]*(prices[i]-prices[i-1])
        value[i]=value[i-1]+pl[i]
    return value,pl,amount

def one_leg_value(principal,prices_mat,signals):
    # function to calculate value change for one leg strategy
    n=len(prices_mat[0])
    amount=np.zeros(n)
    pl=np.zeros(n)
    index = int(abs(signals[0]) - 2)
    amount[0]=(1 if signals[0]>0 else -1)*principal/prices_mat[index,0] if abs(signals[0])>=2 else 0
    amount_open=0
    value=np.zeros(n)
    value[0]=principal
    for i in range(1,n):
        n_trade=0
        if 5>abs(signals[i])>=2:
            index=int(abs(signals[i])-2)
            p=prices_mat[index,i]
            amount_open=principal/p if signals[i]>0 else -principal/p
            amount[i] = amount_open+amount[i-1]
        elif abs(signals[i])<2 and signals[i]!=0:
            amount[i]=0
        elif signals[i]==5:
            amount[i]=amount[i-1]-(amount_open/4.0)
        elif abs(signals[i])==6:
            amount[i]=-amount[i-1]
            amount_open=amount[i]
        else:
            amount[i]=amount[i-1]
        pl[i]=amount[i-1]*(prices_mat[index,i]-prices_mat[index,i-1])
        value[i] = value[i - 1] + pl[i]
    return value,pl,amount







def value_generator(contract,value_list):
    print contract
    principal = 1000000.0
    # a=[x for x in range(100)]
    # print sccontract(a,10)
    all_price, prices = price_concat(contract, '20130101', '20170430')
    price1_series = [x[1] for x in prices]
    price2_series = [x[2] for x in prices]
    price_series = [x[3] for x in prices]
    # volume1_series=[x[4] for x in prices]
    # volume2_series = [x[5] for x in prices]
    op1_series=volume2_series = [x[6] for x in prices]
    op2_series = [x[7] for x in prices]
    date_series = [x[0] for x in prices]
    ma_series_f = sc.get_ma(date_series, contract, all_price, 100)
    ma_series_m = sc.get_ma(date_series, contract, all_price, 300)
    ma_series_s = sc.get_ma(date_series, contract, all_price, 600)
    nbars = [100, 300, 600]
    signal= sc.ma_signal(date_series, contract, all_price, price1_series, price2_series,
                               op1_series,op2_series, nbars)
    values, pl, amount = value(principal, price1_series, price2_series, signal)
    df_price= dict(price=price_series,price1=price1_series,price2=price2_series, amount=amount,maf=ma_series_f,
                   mam=ma_series_m, mas=ma_series_s, signal=signal, pl=pl, value=values / principal)
    # df_price = {'price': price_series, 'maf': ma_series_f, 'm': ma_series_m, 's': ma_series_s, 'sig': signal}
    df_value = {'value': values / principal}
    price_df = pd.DataFrame(data=df_price, index=date_series)
    value_df = pd.DataFrame(data=df_value, index=date_series)
    price_df.to_csv('step_value/'+contract+'wopenint_price.csv')
    value_df.to_csv('step_value/'+contract+'wopenint_value.csv')
    value_list[contract]=value_df
    value_plot(contract,value_df)
    print contract+' finished'
    return 0

def values(contract_list):
    value_list={}
    threads=[]
    for contract in contract_list:
        value_generator(contract,value_list)
    return value_list

def value_plot(contract,df,file_name):
    date_list=df.index.values
    value_list=df['value'].values
    fig=plt.figure()
    net_worth_plot=fig.add_subplot(111)
    net_worth_plot.plot(date_list,value_list)
    fig.autofmt_xdate()
    plt.tight_layout()
    fig.savefig(file_name+'.png',dpi=200)
    plt.close()
