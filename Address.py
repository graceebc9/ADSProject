#!/usr/bin/env python
# coding: utf-8

# In[1]:


# This file contains code for suporting addressing questions in the data

"""# Here are some of the imports we might expect """
import numpy as np
import pandas as pd
from sklearn import linear_model


# # Predict House Price 

# In[2]:


import Assess


# In[ ]:


def predict_house_price(year, lat, lon, prop_type, month= 1, day = 1, year_plus = 2, year_minus = 2, r=0.05):
    """ predicts the house price for fiven inputs, using test data defined in box dimensions r, pulling POI from set radius of 2.2km around each point
    year: year of price to predict 
    lat, lon: latitude and longitude of price to predict
    prop_type: property type to predict 
    month, day: used to set date to define the time ring around which we pull test data 
    year_plus, year_minus: the size fo the time ring which is pulled 
    r: radius around the test point in which we pull test data
    """
    df, test_point = Assess.pull_price_data(lat = lat, lon= lon , year = year , month = month, day = day ,prop_type = prop_type ,  year_plus = year_plus , year_minus = year_minus ,    r=r  )
    y, X, name = Assess.create_data_with_POI(df)
    size_td = df.shape[0]

    model = linear_model.LinearRegression()
    model.fit(X,y)
    
    
    #create X for test data 
    #this assumes that data does not include the given data - extension would be to check 
    POI = Assess.pull_POI_single(lat, lon)
    L = test_point  +  POI
    x = np.reshape(L, (-1, 1)).T
    X_test = pd.DataFrame(x, columns = name) 

    #make prediction and give size of the test data
    price_predict = model.predict(X_test)
    
    return price_predict, size_td
    
    
    
    


# In[ ]:


def predict_house_price_2(df, test_point):
    """ this is used when database space is low, pull your dataframe seperately and download it, then input into this function  
    """
    y, X, name = Assess.pull_poi(df)
    size_td = df.shape[0]

    model = linear_model.LinearRegression()
    model.fit(X,y)
    
    
    #create X for test data 
    #this assumes that data does not include the given data - extension would be to check 
    POI = Assess.pull_POI_single( lat, lon, r)
    L = test_point  +  POI
    x = np.reshape(L, (-1, 1)).T
    X_test = pd.DataFrame(x, columns = name) 

    price_predict = model.predict(X_test)
    
    return price_predict, size_td
    
    
    

