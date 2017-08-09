import numpy as np
import data_processing as dp
from datetime import datetime,time

def ma(prices, n_bars, index=None):
    if len(prices) < n_bars:
        return 0
    else:
        return np.average(prices[-n_bars:])

def get_ma(dates, contract, price_data, n_bars):
    n = len(dates)
    ma_array = np.zeros(n)
    for i in range(n):
        date = dates[i]
        price_near = price_data[dp.main_contract(date, contract)[0]].loc[:date][-n_bars:]
        price_far = price_data[dp.main_contract(date, contract)[1]].loc[:date][-n_bars:]
        price_far = price_far['closeprice']
        price_near = price_near['closeprice']
        price_diff = np.diff([price_far, price_near], axis=0)[0]
        ma_array[i] = ma(price_diff, n_bars)
    return ma_array

def ma_signal(dates, contract, price_data, prices1,prices2,op1,op2, n_bars):
    #signal generator for calendar spread strategy
    n = len(dates)
    start = max(n_bars) - 1
    ma_f = get_ma(dates, contract, price_data, n_bars[0])
    ma_m = get_ma(dates, contract, price_data, n_bars[1])
    ma_s = get_ma(dates, contract, price_data, n_bars[2])
    start_month_range=[11,3,7]
    start_day_range=[14,15,16,17]
    signal = np.zeros(len(dates))
    flag_open = 0
    open_price_ratio = 0
    open_price=0
    step_price=0
    flag_start=0
    stop_point=9999.0
    end_time_set=[time(15,00,00),time(23,30,00),time(23,45,00),time(00,00,00)]
    for i in range(start, n):
        price1=float(prices1[i])
        price2=float(prices2[i])
        openint1=op1[i]+1
        openint2=op2[i]+1

        #
        if openint2/openint1>=1.0/3.0 and flag_start==0:
            flag_start=1
        # if (dates[i].month in start_month_range) and (dates[i].day in start_day_range):
        #     flag_start=1
        if flag_start:
            price = price1-price2
            date = dates[i]
            if i==(n-1):
                date_next=date
            else:
                date_next = dates[i + 1]
            ma_fast = ma_f[i]
            ma_medium = ma_m[i]
            ma_slow = ma_s[i]
            last_month = [12, 4, 8]  # the month before expiration
            mx = max([ma_fast, ma_medium, ma_slow])
            mn = min([ma_fast, ma_medium, ma_slow])
            if (mx==ma_fast) and (price > mx) and (0 == flag_open):
                # if no position now.. open a long
                signal[i] = 2
                flag_open = 1
                open_price_ratio = price1/price2
                open_price=price
                step_price=price
                stop_point = max(price1, price2) * 0.02
            elif (mn==ma_fast) and (price < mn) and (flag_open == 0):
                # if no position now, open a short
                signal[i] = -2
                flag_open = -1
                open_price_ratio = price1/price2
                open_price=price
                step_price = price
                stop_point = max(price1, price2) * 0.02

            elif (flag_open == 1) and (price < ma_medium):
                # close the opened long
                signal[i] = -1.8
                flag_open = 0
            elif (flag_open == -1) and (price > ma_medium):
                # close the opened short
                signal[i] = 1.8
                flag_open = 0

            elif ((date.month in last_month) and (date_next.month != date.month)) or i==n:
                # if approaching the expiration month
                if flag_open == 1:
                    signal[i] = -1.6
                    flag_open = 0
                elif flag_open == -1:
                    signal[i] = 1.6
                    flag_open = 0
                flag_start=0


            elif (flag_open == 1) and ((open_price-price)>=stop_point):
                signal[i] = -1.4
                flag_open = 0

            elif (flag_open == -1) and ((price-open_price)>=stop_point):
                signal[i] = 1.4
                flag_open = 0

            elif (flag_open == 1) and ((price-step_price) >= 2*stop_point):
                signal[i]=3
                step_price=price
            elif (flag_open == -1) and ((step_price-price) >= 2*stop_point):
                signal[i]=3
                step_price=price

    return signal

def spot_signal(rys,reverse=False,step=False,day_adjust=False, stop=0.02,bias=0.0,tolerance_factor=0.1):
    #signal generator for spot future strategy
    dates = [x[0] for x in rys]
    rys2=[x[11] for x in rys]
    rys3 = [x[12] for x in rys]



    prices1=[x[1] for x in rys]
    prices2=[x[2] for x in rys]
    prices3 = [x[3] for x in rys]

    spots1=[x[4] for x in rys]
    spots2 = [x[5] for x in rys]
    spots3 = [x[6] for x in rys]

    dleft1 = [x[7] for x in rys]
    dleft2 = [x[8] for x in rys]
    dleft3 = [x[9] for x in rys]

    openints1=[x[13] for x in rys]
    openints2 = [x[14] for x in rys]
    openints3 = [x[15] for x in rys]

    max1_=[x[16] for x in rys]
    max2_ = [x[17] for x in rys]
    max3_ = [x[18] for x in rys]

    signal=np.zeros(len(dates))
    flag_open=0
    stop_flag=0
    flag_start=0
    wrong_direction_count=0
    last_month = [12, 4, 8]
    n=len(dates)
    for i in range(n):
        dates[i]=datetime.strptime(dates[i],'%Y%m%d')
    # this part is for RY strategy, not studying it currently
    # for i in range(n):
    #     if i == (n - 1):
    #         date_next = date
    #     else:
    #         date_next = dates[i + 1]
    #     date=dates[i]
    #     price2,price3=(prices2[i],prices3[i])
    #     price=price2-price3
    #     ry2=rys2[i]
    #     ry3=rys3[i]
    #     if ry2-ry3>=0.21 and flag_open==0:
    #         signal[i]=-2
    #         flag_open=-1
    #         open_price = price
    #         stop_point = open_price * 0.02
    #     elif flag_open==-1 and price-open_price>=stop_point:
    #         signal[i]=1.4
    #         flag_open=0
    #     elif ry2-ry3<=-0.59 and flag_open==0:
    #         signal[i]=2
    #         flag_open=1
    #         open_price = price
    #         stop_point = open_price * 0.02
    #     elif flag_open==1 and open_price-price>=stop_point:
    #         signal[i]=-1.4
    #         flag_open=0
    #     elif ((date.month in last_month) and (date_next.month != date.month)) or i==n:
    #         # if approaching the expiration month
    #         if flag_open == 1:
    #             signal[i] = -1.6
    #             flag_open = 0
    #         elif flag_open == -1:
    #             signal[i] = 1.6
    #             flag_open = 0
    #     elif -0.59<=(ry2-ry3)<=0.21 and flag_open==1:
    #         signal[i]=1.2
    #         flag_open=0
    for i in range(n):
        if i == (n - 1):
            date_next = date
        else:
            date_next = dates[i + 1]
        date=dates[i]

        if flag_open==0:
            main_contract = np.argmax([openints1[i],openints2[i],openints3[i]])
            openint=max([openints1[i],openints2[i],openints3[i]])
            signal_to_open = main_contract + 2
        main_dict = [(prices1[i], spots1[i],max1_[i],dleft1[i]), (prices2[i], spots2[i],max2_[i], dleft2[i]), (prices3[i], spots3[i],max3_[i], dleft3[i])]
        price,spot,maxpos_,dleft=main_dict[main_contract]
        tolerance=spot*tolerance_factor
        tolerance2 = spot * 0.08
        # if openint <= 0.75 * maxpos_ or openint2>=openint1*0.5:
        #     start_flag=1


        if (price-spot-bias)>tolerance and flag_open==0 and stop_flag==0:
            signal[i]=-signal_to_open
            flag_open=-1
            open_price = price
            stop_point = open_price * stop
            step_price=price

        elif flag_open==-1 and price-open_price>=stop_point:
            signal[i]=1.4
            flag_open=0
            wrong_direction_count+=1
            if reverse==False:
                stop_flag=1
            if reverse==True:
                if wrong_direction_count<2:
                    signal[i]=6
                    flag_open=1
                    open_price = price
                    stop_point = open_price * stop
                    step_price = price
                elif wrong_direction_count==2:
                    wrong_direction_count=0
                    stop_flag=1
        elif (spot-price-bias)>tolerance and flag_open==0 and stop_flag==0:
            signal[i]=signal_to_open
            flag_open=1
            open_price = price
            stop_point = open_price * stop
            step_price=price
        elif flag_open==1 and open_price-price>=stop_point:
            signal[i]=-1.4
            flag_open=0
            if reverse == False:
                stop_flag=1
            wrong_direction_count += 1
            if reverse==True:
                if wrong_direction_count<2:
                    signal[i]=-6
                    flag_open=-1
                    open_price = price
                    stop_point = open_price * stop
                    step_price = price
                elif wrong_direction_count==2:
                    wrong_direction_count=0
                    stop_flag=1
        # elif np.argmax([openints1[i],openints2[i],openints3[i]])!=main_contract and flag_open!=0:
        #     if flag_open == 1:
        #         signal[i] = -1.6
        #         flag_open = 0
        #     elif flag_open == -1:
        #         signal[i] = 1.6
        #         flag_open = 0
        elif ((date.month in last_month) and (date_next.month != date.month)) or i==n:
            stop_flag=0
            # if approaching the expiration month
            if flag_open == 1:
                signal[i] = -1.6
                flag_open = 0
            elif flag_open == -1:
                signal[i] = 1.6
                flag_open = 0
        elif -tolerance<=(price-spot-bias)<=tolerance and flag_open==1:
            signal[i]=1.2
            flag_open=0
        if step==True:
            if (flag_open == 1) and ((price - step_price) >= 2 * stop_point):
                signal[i] = 5
                step_price = price
            elif (flag_open == -1) and ((step_price - price) >= 2 * stop_point):
                signal[i] = 5
                step_price = price
    return signal

def spot_spread_signal(rys):
    #calendar spread strategy looking at spot future difference
    dates = [x[0] for x in rys]
    rys2=[x[11] for x in rys]
    rys3 = [x[12] for x in rys]

    prices1=[x[1] for x in rys]
    prices2=[x[2] for x in rys]
    prices3 = [x[3] for x in rys]

    spots1=[x[4] for x in rys]
    spots2 = [x[5] for x in rys]
    spots3 = [x[6] for x in rys]

    openints1=[x[13] for x in rys]
    openints2 = [x[14] for x in rys]
    openints3 = [x[15] for x in rys]

    max1_=[x[16] for x in rys]
    max2_ = [x[17] for x in rys]
    max3_ = [x[18] for x in rys]

    signal=np.zeros(len(dates))
    flag_open=0
    start_flag=0
    stop_flag=0
    last_month = [12, 4, 8]
    n=len(dates)
    for i in range(n):
        dates[i]=datetime.strptime(dates[i],'%Y%m%d')
    for i in range(10,n):
        if i == (n - 1):
            date_next = date
        else:
            date_next = dates[i + 1]
        date=dates[i]
        # if flag_open==0:
        #     main_contract = np.argmax([openints1[i],openints2[i],openints3[i]])
        #     signal_to_open = main_contract + 2
        # main_dict = [(prices1[i], spots1[i],max1_[i]), (prices2[i], spots2[i],max2_[i]), (prices3[i], spots3[i],max3_[i])]
        price1,spot1,openint1,maxpos1_=(prices1[i], spots1[i], openints1[i],max1_[i])
        price2, spot2,openint2, maxpos2_ = (prices2[i], spots2[i],openints2[i], max2_[i])
        price=price1-price2
        tolerance=price1*0.1

        if openint1 <= 0.75 * maxpos1_ or openint2>=openint1*0.5:
            start_flag=1

        if price1-spot1>tolerance and flag_open==0 and stop_flag==0 and start_flag==1:
            signal[i]=-2
            flag_open=-1
            open_price = price
            stop_point = open_price * 0.02
        elif flag_open==-1 and price-open_price>=stop_point:
            signal[i]=1.4
            flag_open=0
            # stop_flag=1
        elif spot1-price1>tolerance and flag_open==0 and stop_flag==0:
            signal[i]=2
            flag_open=1
            open_price = price
            stop_point = open_price * 0.02
        elif flag_open==1 and open_price-price>=stop_point:
            signal[i]=-1.4
            flag_open=0
            # stop_flag=1
        elif ((date.month in last_month) and (date_next.month != date.month)) or i==n:
            # stop_flag=0
            # if approaching the expiration month
            if flag_open == 1:
                signal[i] = -1.6
                flag_open = 0
            elif flag_open == -1:
                signal[i] = 1.6
                flag_open = 0
        elif -tolerance<=(price1-spot1)<=tolerance and flag_open==1:
            signal[i]=1.2
            flag_open=0

    return signal