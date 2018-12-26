#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import scipy.cluster.hierarchy as shc
import matplotlib.pyplot as plt
import statistics as stat

from matplotlib.font_manager import FontProperties
from sklearn.cluster import KMeans
from sklearn.manifold import MDS
from sklearn.cluster import AgglomerativeClustering
from sklearn import manifold
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from abc import ABCMeta, abstractmethod

get_ipython().run_line_magic('matplotlib', 'inline')
plt.rcParams['axes.unicode_minus']=False
engine = create_engine('sqlite:///fund.db')


class ProfitVisualize(metaclass=ABCMeta):
    
    '''
    input:
        month_NAV：該月所有淨值
        random_names：基金池的所有基金名
    output:
        整理出的features
        與features對齊的基金名
    '''
    @abstractmethod
    def getFeatures(self, NAV,names):
        pass
    
    '''
    input:回測年
    output:基金池（名字）
    '''
    @abstractmethod
    def poolDecide(self, year):
        pass
    
    def getNAV(self,names,start,end):
        data = pd.read_sql(sql='select * from price where date between ? and ? order by date asc',
                                 con=engine,index_col='date', params=[start,end])
        date = pd.read_sql(sql='select distinct date from price where date between ? and ? order by date asc',
                                 con=engine,index_col='date', params=[start,end]).index
        NAV = np.zeros((len(names),len(date)))
        for j in range (len(names)):
            temp = data[data['id'] == names[j]]
            NAV[j][0] = temp.iloc[0]['NAV']
            for i,day in enumerate(date[1:]):
                try:
                    NAV[j][i+1] = temp.loc[day]['NAV']
                except:
                    NAV[j][i+1] = NAV[j][i]
        return NAV
        
    def __init__(self,clusterStrategy):
        self.clusterStrategy = clusterStrategy
    
    def getProfitPicture(self):
        year = input("請輸入欲回測年：")        
        names = self.poolDecide(year)
        NAV = self.getNAV(names,year+'-01-01',year+'-01-31')
        features,names,dissimilarity = self.getFeatures(NAV,names)
        clustering = ClusterMethod(self.clusterStrategy).startClustering(features)
        
        mds = MDS(n_components=2, dissimilarity=dissimilarity, n_jobs=8).fit(features).embedding_
        plt.figure(figsize=(15, 15))
        plt.subplots_adjust(bottom=0.1)
        plt.scatter(mds[:, 0], mds[:, 1], c=clustering.labels_)
        plt.show()
        
        camp = pd.DataFrame(data=clustering.labels_, index=names,columns=['label'])
        choose_name = []
        for i in range(4):
            choose_name.append(camp[camp['label'] == i].sample(n=1).index[0])
        choose_name.append('0050 元大台灣50')
        
        NAV = self.getNAV(choose_name,year+'-01-01',year+'-12-31')        
        rate = np.zeros((len(choose_name),len(NAV[0])-1))
        for j in range (len(choose_name)):
            for i in range (len(NAV[0])-1):
                rate[j][i] = (NAV[j][i+1] - NAV[j][i]) / NAV[j][i]

        choose_rate = []
        for i in range(len(rate[0])):
            temp = (rate[0][i] + rate[1][i] + rate[2][i] + rate[3][i])/4
            choose_rate.append(temp)
        
        plt.figure(figsize=(13, 13))
        plt.ylabel('漲跌幅')
        plt.title('漲跌幅對比')
        plt.plot(choose_rate)
        plt.plot(rate[-1])
        plt.legend(['choose','compare'])
        plt.show()
        
        choose_profit = []
        compare__profit = []
        start = (NAV[0][0] + NAV[1][0] + NAV[2][0] + NAV[3][0])/4
        for i in range(len(NAV[0])):
            temp = (NAV[0][i] + NAV[1][i] + NAV[2][i] + NAV[3][i])/4
            temp = (temp-start)/start*100
            choose_profit.append(temp)
            compare__profit.append((NAV[4][i]-NAV[4][0])/NAV[4][0]*100)
            
        plt.figure(figsize=(14, 14))
        plt.ylabel('收益率')
        plt.title('收益率對比')
        plt.plot(choose_profit)
        plt.plot(compare__profit)
        plt.legend(['Choose','Compare'])
        plt.show()

class ClusterStrategy(metaclass=ABCMeta):
    @abstractmethod
    def Clustering(self,features):
        pass

class ClusterMethod:
    def __init__(self, clusterStrategy):
        self.clusterStrategy = clusterStrategy
    
    def startClustering(self,features):
        return self.clusterStrategy.Clustering(self,features)

class K_Means(ClusterStrategy):
    def Clustering(self,features):
        return KMeans(n_clusters=4).fit(features)

class Hierarchical(ClusterStrategy):
    def Clustering(self,features):
        return AgglomerativeClustering(n_clusters=4).fit(features)
