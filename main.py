import data_processing as dp
import pandas as pd
import numpy as np
import signal_calculator as sc
import matplotlib.pyplot as plt

if __name__ == '__main__':
    # contract_list=['ag','au','al','cu','y','bu', 'zn', 'pp', 'l', 'TA', 'rb', 'j', 'jm', 'v', 'jd', 'm', 'RM', 'OI',
    #                'p' ,'FG','CF', 'SR', 'i', 'hc', 'ZC', 'ru', 'c', 'cs']
    contract_list=['bu', 'zn', 'pp', 'l', 'TA', 'rb', 'j', 'jm', 'v', 'jd', 'm', 'RM', 'OI',
                   'p' ,'FG','CF', 'SR', 'i', 'hc','ZC', 'ru', 'c', 'cs']
    totoal_amount=len(contract_list)*1000000.0
    print totoal_amount
    value_list=[]
    for contract in contract_list:
        print contract
        rys=dp.price_concat(contract,'20130101','20170801',freq='Daily')
        dates = [x[0] for x in rys]
        price1=[x[1] for x in rys]
        price2=[x[2] for x in rys]
        price3 = [x[3] for x in rys]
        spot_price1=[x[4] for x in rys]
        spot_price2=[x[5] for x in rys]
        spot_price3 = [x[6] for x in rys]
        avg = np.mean([(price - spot) / spot for price, spot in zip(price1, spot_price1)])
        std=np.std([(price - spot)/spot for price, spot in zip(price1, spot_price1)])
        signals = sc.spot_signal(rys, stop=0.05)
        d_left1=[x[7] for x in rys]
        d_left2=[x[8] for x in rys]
        d_left3 = [x[9] for x in rys]
        ry1=[x[10] for x in rys]
        ry2=[x[11] for x in rys]
        ry3 = [x[12] for x in rys]
        price_mat=np.array([price1,price2,price3])
        value,pl,amount=dp.one_leg_value(1000000.0,price_mat,signals)
        pl_name=contract+'pl'
        df=pd.DataFrame({pl_name : pl})
        df.set_index(pd.DatetimeIndex(dates), inplace=True)
        value_list.append(df)
    df_sum=pd.concat(value_list,join='outer',axis=1)
    df_sum.fillna(0)
    pl_sum=df_sum.sum(axis=1).values
    df_sum['pl']=pl_sum
    values=np.zeros([len(df_sum)])
    values[0]=totoal_amount+pl_sum[0]
    for i in range(1,len(values)):
        values[i]=pl_sum[i]+values[i-1]
    df_sum['values']=values/totoal_amount
    file_name = 'value_sum/sum_0.05'
    df_sum.to_csv(file_name+'.csv')
