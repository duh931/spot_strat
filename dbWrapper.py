import psycopg2
import pandas as pd
import numpy as np

class dbWrapper:
    def __init__(self,shost):
        self.conn = psycopg2.connect(host=shost, port=5432, user='postgres', password='123456', database='history_et_db')
        self.cur = self.conn.cursor()

    def getBars(self,sSymbol,sBDay,sEDay,sBarType):
        sSQL = "select tradingday, bartime, openprice, highprice, lowprice, closeprice, volume, openinterest from china_fut." + sSymbol + " where tradingday >= %s  and tradingday <= %s and bartype = %s  and bartime >= %s and bartime <= %s order by tradingday,id asc;"
        self.cur.execute(sSQL,(str(sBDay),str(sEDay),sBarType,'08:00','16:00'))
        Bars = self.cur.fetchall()
        dfBars = pd.DataFrame(Bars)
        if len(dfBars)==0:
            return pd.DataFrame()
        dfBars.columns = ['tradingday', 'bartime', 'openprice', 'highprice', 'lowprice', 'closeprice', 'volume','openinterest']
        dfBars[['openprice', 'highprice', 'lowprice', 'closeprice']] = dfBars[['openprice', 'highprice', 'lowprice', 'closeprice']].astype(float)
        dfBars[['openinterest']] = dfBars[['openinterest']].astype(int)
        dfBars[['bartime']] = dfBars[['bartime']].astype(str)
        return dfBars

    def getNightBars(self,sSymbol,sBDay,sEDay,sBarType):
        sSQL = "select tradingday, bartime, openprice, highprice, lowprice, closeprice, volume, openinterest from china_fut." + sSymbol + " where tradingday >= %s  and tradingday <= %s and bartype = %s  and (bartime >= %s or bartime <= %s) order by tradingday,id asc;"
        self.cur.execute(sSQL,(str(sBDay),str(sEDay),sBarType,'20:00','02:31'))
        Bars = self.cur.fetchall()
        dfBars = pd.DataFrame(Bars)
        if len(dfBars)==0:
            return pd.DataFrame()
        dfBars.columns = ['tradingday', 'bartime', 'openprice', 'highprice', 'lowprice', 'closeprice', 'volume','openinterest']
        dfBars[['openprice', 'highprice', 'lowprice', 'closeprice']] = dfBars[['openprice', 'highprice', 'lowprice', 'closeprice']].astype(float)
        dfBars[['openinterest']] = dfBars[['openinterest']].astype(int)
        dfBars[['bartime']] = dfBars[['bartime']].astype(str)
        return dfBars

    def highprice(self, x):
        if x['highprice_y'] > x['highprice_x']:
            return x['highprice_y']
        else:
            return x['highprice_x']

    def lowprice(self, x):
        if x['lowprice_y'] < x['lowprice_x']:
            return x['lowprice_y']
        else:
            return x['lowprice_x']
    def openprice(self, x):
        if pd.isnull(x['openprice_y']):
            return x['openprice_x']
        else:
            return x['openprice_y']

    def getFullDayBars(self, sSymbol, sBDay, sEDay):
        nightbar = self.getNightBars(sSymbol, sBDay, sEDay, 'Daily')
        daybar = self.getBars(sSymbol, sBDay, sEDay, 'Daily')
        bar = pd.merge(daybar, nightbar, how='left', on=['tradingday'])
        bar['openprice'] = bar.apply(self.openprice,axis=1)
        bar['highprice'] = bar.apply(self.highprice,axis=1)
        bar['lowprice'] = bar.apply(self.lowprice,axis=1)
        bar['closeprice'] = bar['closeprice_x']
        bar = bar[['tradingday', 'bartime_x', 'openprice', 'highprice', 'lowprice', 'closeprice', 'volume_x']]
        bar.columns = ['tradingday', 'bartime', 'openprice', 'highprice', 'lowprice', 'closeprice', 'volume']
        return bar

    def getBarsbyDay(self,sSymbol):
        sSQL = "select tradingday, bartime, openprice, highprice, lowprice, closeprice, volume from china_fut." + sSymbol + " where bartype = %s and bartime >= %s and bartime <= %s order by tradingday asc;"
        print(sSQL)
        self.cur.execute(sSQL, ('Daily','08:00','16:00',))
        Bars = self.cur.fetchall()
        dfBars = pd.DataFrame(Bars)
        dfBars.columns = ['tradingday', 'bartime', 'openprice', 'highprice', 'lowprice', 'closeprice', 'volume']
        dfBars[['openprice', 'highprice', 'lowprice', 'closeprice']].astype(float)
        return dfBars
    def getSpotPrice(self,sProductID,sBDay,sEDay):
        sSQL = "select tradingday, actprice from china_fut.contract_actual where productID = %s and tradingday >= %s and tradingday <= %s order by tradingday asc;"
        self.cur.execute(sSQL, (sProductID,str(sBDay),str(sEDay),))
        Bars = self.cur.fetchall()
        dfBars = pd.DataFrame(Bars)
        dfBars.columns = ['tradingday', 'spotprice']
        dfBars[['spotprice']] = dfBars[['spotprice']].astype(float)
        dfBars[['tradingday']] = dfBars[['tradingday']].astype(str)
        return dfBars


class recordDB:
    def __init__(self,shost):
        self.conn = psycopg2.connect(host=shost, port=5432, user='postgres', password='123456', database='record_db')
        self.cur = self.conn.cursor()

    def getPosition(self,sAccID,sBDay,sEDay):
        sSQL = "select tradingday, symbol, side, postotal from account.a" + sAccID + "_position where tradingday >= %s  and tradingday <= %s order by tradingday,id asc;"
        self.cur.execute(sSQL,(str(sBDay),str(sEDay)))
        pos = self.cur.fetchall()
        dfPos = pd.DataFrame(pos)
        if len(dfPos)==0:
            return pd.DataFrame()
        return dfPos

# DEMO
dd = dbWrapper('192.168.10.188')
# sBarType='1 Min' , '2 Min', '3 Min', '5 Min', '15 Min', '1 Hour', 'Daily'
# datas1 = dd.getSpotPrice('CF','20130101','20130501')
# datas2 = dd.getBars('CF509','20150820','20150831','Daily')
# print datas1
# print datas2