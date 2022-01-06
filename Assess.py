#!/usr/bin/env python
# coding: utf-8

# In[12]:


import mysql.connector 

import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
import pandas as pd
import osmnx as ox
import numpy as np 


# In[13]:


#connect to db 
import databaseconfig as cfg

connection =   mysql.connector.connect( user=cfg.USR, password=cfg.PASSWORD, database=cfg.DBNAME,  host=cfg.ENDPOINT , port =cfg.PORT, allow_local_infile = True, autocommit = True) 
cursor = connection.cursor()


# In[20]:


#define the tags we want to pull for POI to use in predicting price
dict_tags = { 'total' : {"amenity": True, 
                        "buildings": True, 
                        "historic": True, 
                        "leisure": True, 
                        "shop": True, 
                        "tourism": True,
                        "healthcare": True} ,
        'edu': {"amenity" : 'school'} , 
        'n_life': {"amenity": ['brothel', 'casino', 'gambling', 'stripclub' ]} 
        } 


# In[19]:


def count_amen(h_lat, h_lon, tags):
    """count the amentities surrounding a lat long from OSM - count total POI around lat lon r = radius of box; 2.2km default
    """
    r= 0.02
    box_width = r # About 2.2 km
    box_height = r
    north = h_lat + box_height/2
    south = h_lat - box_height/2
    west = h_lon - box_width/2
    east = h_lon + box_width/2
    pois = ox.geometries_from_bbox(north, south, east, west, tags)
    count = len(pois) #total number of POI around house  
    return count


# In[28]:


def pull_POI_single(lat, lon):
    """ pulls the POI for the single point - used to create the test data 
    """
    r=0.02
    L = [ count_amen(lat,lon, tag, r) for tag in dict_tags.values() ]
    return L


# In[30]:


def pull_price_data(lat, lon , year, prop_type ,month =1 , day= 1,   year_plus = 2 , year_minus = 2 ,    r=0.02  ) :
    """pulls the price data df and gives the test point from input
    
    year: year of price to predict 
    lat, lon: latitude and longitude of price to predict
    prop_type: property type to predict 
    month, day: used to set date to define the time ring around which we pull test data 
    year_plus, year_minus: the size fo the time ring which is pulled 
    r: radius around the test point in which we pull test data
    """
    #pull space and time box
    date_var = datetime.date(year,month ,day )

    datemax = date_var + relativedelta(years = year_plus ) 
    datemin = date_var - relativedelta(years=year_minus ) 
 
    box_width = r 
    box_height = r

    
    north = lat + box_height/2
    south = lat - box_height/2
    west = lon - box_width/2
    east = lon + box_width/2


    """ find the lat, lon, property type, price and date of transfer of all properties in box defined by the nsew vectors""" 

    query = """select a.latitude, a.longitude, b.price, b.property_type, b.date_of_transfer from 
                (select latitude, longitude, postcode, db_id, country from postcode_data 
                where latitude <=   %(north)s
                and latitude >= %(south)s
                and longitude <= %(east)s
                and longitude >=  %(west)s  ) a 
                join (select * from pp_data
                where date_of_transfer < %(datemax)s
                and  date_of_transfer > %(datemin)s
                and property_type = %(prop_type)s) b 
                on a.postcode = b.postcode"""
    cursor.execute(query, {'north' : north , 'south': south, 'east': east, 'west': west , 'datemax' : datemax , 'datemin':  datemin, 'prop_type' : prop_type })
    read23 = cursor.fetchall()
    df = pd.DataFrame(read23)
    df['year'] = pd.DatetimeIndex(df[4]).year
    df['month'] = pd.DatetimeIndex(df[4]).month
    df['day'] = pd.DatetimeIndex(df[4]).day
    
    test_point = [lat, lon, year, month, day]
    #if df.shape[0] < 500:
     #   raise ValueError("Number of training data less than 500 - {}".format(df.shape[0]) )
    
    return df, test_point
  


# In[17]:


def create_data_with_POI(df):
    """This function pulls points of interests from OSM, and creates the labelled data needed for price prediction.
    > You can update the dict_tags to create extra features. 
    Here we define Total Amenities, Education, and Nightlife Factors. Code is set up to work with any number of dict_tags
    df: df from pull price function
    """
    #find total POI
    latlon = df.iloc[:,0:2]
    
    dict_tags = { 'total' : {"amenity": True, 
                            "buildings": True, 
                            "historic": True, 
                            "leisure": True, 
                            "shop": True, 
                            "tourism": True,
                            "healthcare": True} ,
            'edu': {"amenity" : 'school'} , 
            'n_life': {"amenity": ['brothel', 'casino', 'gambling', 'stripclub' ]} 
            } 
    
    L = [ count_amen(float(x[1][0]),float(x[1][1]), tag) for tag in dict_tags.values()  for x in  latlon.iterrows()   ]

    #reformat POI and DF into y,X
    poi = np.array_split(L, len(dict_tags) ) 
    
    i= 1
    
    for a in poi:
        df_p = pd.DataFrame(a)
        df[str(i)] = df_p
        i = i+1
    
    #define variables 
    y= df.iloc[: , 2] 
    X = pd.concat( [latlon, df.iloc[: , 5:] ]  , axis =1 )
   
    name = ['lat', 'lon', 'year', 'month', 'day'] +  [*dict_tags]

    y.columns = 'price' 
    X.columns = name
    
    return y, X, name

