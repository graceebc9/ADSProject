#!/usr/bin/env python
# coding: utf-8

# In[7]:


import urllib.request
import requests 
import pandas as pd
import mysql.connector 
import osmnx as ox
import numpy as np

# This file accesses the data


# In[8]:


#connect to db 
import databaseconfig as cfg
connection = cfg.connection
cursor = cfg.cursor


# In[4]:


def load_price_data_sql():
    #Create tables to store price data from gov land registry 
    query = """
    DROP TABLE IF EXISTS `pp_data`;
    CREATE TABLE IF NOT EXISTS `pp_data` (
      `transaction_unique_identifier` tinytext COLLATE utf8_bin NOT NULL,
      `price` int(10) unsigned NOT NULL,
      `date_of_transfer` date NOT NULL,
      `postcode` varchar(8) COLLATE utf8_bin NOT NULL,
      `property_type` varchar(1) COLLATE utf8_bin NOT NULL,
      `new_build_flag` varchar(1) COLLATE utf8_bin NOT NULL,
      `tenure_type` varchar(1) COLLATE utf8_bin NOT NULL,
      `primary_addressable_object_name` tinytext COLLATE utf8_bin NOT NULL,
      `secondary_addressable_object_name` tinytext COLLATE utf8_bin NOT NULL,
      `street` tinytext COLLATE utf8_bin NOT NULL,
      `locality` tinytext COLLATE utf8_bin NOT NULL,
      `town_city` tinytext COLLATE utf8_bin NOT NULL,
      `district` tinytext COLLATE utf8_bin NOT NULL,
      `county` tinytext COLLATE utf8_bin NOT NULL,
      `ppd_category_type` varchar(2) COLLATE utf8_bin NOT NULL,
      `record_status` varchar(2) COLLATE utf8_bin NOT NULL,
      `db_id` bigint(20) unsigned NOT NULL
    ) DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=1 ;
    """

    cursor.execute(query, multi = True)

    query=""" ALTER TABLE `pp_data`
            ADD PRIMARY KEY (`db_id`);
            MODIFY `db_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=1;
            CREATE INDEX `pp.postcode` USING HASH
            ON `pp_data`
            (postcode);
            CREATE INDEX `pp.date` USING HASH
            ON `pp_data` 
            (date_of_transfer);"""

    cursor.execute(query, multi = True)

    #Download  all files
    year_list = range(1995,2022)

    filename1 = ["http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-{0}-part1.csv".format(year) for year in year_list]
    filename2 =  ["http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-{0}-part2.csv".format(year) for year in year_list] 
    filenames= filename1 + filename2 


    for url in filenames:
        data = pd.read_csv(url)   
        name = url[-15:]
        df = pd.DataFrame(data)
        df = df.iloc[: , 1:]
        df.to_csv('{}'.format(name))
    
    #load data into databse 
    for url in filenames:
        name = url[-15:]
        query = "LOAD DATA local INFILE " + "'{}'".format(name)  + """ INTO TABLE property_prices.pp_data 
                    FIELDS TERMINATED BY ',' 
                    ENCLOSED BY ''
                    LINES TERMINATED BY '\n'; """
        cursor.execute(query)

    connection.commit()  
    
    #test sql load  
    query = "select count(distinct transaction_unique_identifier) from property_prices.pp_data ;"
    cursor.execute(query)
    head_rows = cursor.fetchmany()
    assert head_rows == 675635, "Count of distinct trx_uni_id should be 675635"


# In[5]:


def load_postcode_data(postcode_csv):
    """pull postcode data, convert into dataframe, load to sql, and return the dataframe
    postcode_csv = location of csv without columns """
    
    query = """DROP TABLE IF EXISTS `property_prices.postcode_data`;
                    CREATE TABLE IF NOT EXISTS `property_prices.postcode_data` (
                      `postcode` varchar(8) COLLATE utf8_bin NOT NULL,
                      `status` enum('live','terminated') NOT NULL,
                      `usertype` enum('small', 'large') NOT NULL,
                      `easting` int unsigned,
                      `northing` int unsigned,
                      `positional_quality_indicator` int NOT NULL,
                      `country` enum('England', 'Wales', 'Scotland', 'Northern Ireland', 'Channel Islands', 'Isle of Man') NOT NULL,
                      `latitude` decimal(11,8) NOT NULL,
                      `longitude` decimal(10,8) NOT NULL,
                      `postcode_no_space` tinytext COLLATE utf8_bin NOT NULL,
                      `postcode_fixed_width_seven` varchar(7) COLLATE utf8_bin NOT NULL,
                      `postcode_fixed_width_eight` varchar(8) COLLATE utf8_bin NOT NULL,
                      `postcode_area` varchar(2) COLLATE utf8_bin NOT NULL,
                      `postcode_district` varchar(4) COLLATE utf8_bin NOT NULL,
                      `postcode_sector` varchar(6) COLLATE utf8_bin NOT NULL,
                      `outcode` varchar(4) COLLATE utf8_bin NOT NULL,
                      `incode` varchar(3)  COLLATE utf8_bin NOT NULL,
                      `db_id` bigint(20) unsigned NOT NULL
                    ) DEFAULT CHARSET=utf8 COLLATE=utf8_bin;"""

    cursor.execute(query, multi=True)
    query = """
                    ALTER TABLE `property_prices.postcode_data`
                    ADD PRIMARY KEY (`db_id`);
                    MODIFY `db_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=1;
                    CREATE INDEX `po.postcode` USING HASH
                      ON `postcode_data`
                        (postcode);
                        """
    cursor.execute(query, multi=True)


    #load data 
    cols = ['postcode','status','usertype','easting','northing','positional_quality_indicator','country','latitude','longitude','postcode_no_space','postcode_fixed_width_seven','postcode_fixed_width_eight','postcode_area','postcode_district','postcode_sector','outcode','incode']
    data = pd.read_csv(postcode_csv, names =cols)  
    post_df = pd.DataFrame(data)
    post_df.to_csv('postcodes.csv')
    
    
    # load postcode data to sql 
    name = 'postcodes.csv'
    query = "LOAD DATA local INFILE " + "'{}'".format(name)  + """ INTO TABLE property_prices.postcode_data 
                FIELDS TERMINATED BY ',' 
                ENCLOSED BY ''
                LINES TERMINATED BY '\n'; """
    cursor.execute(query)
    connection.commit()
    
    query = "select count(*) from postcode_data;"
    cursor.execute(query)
    post_records = cursor.fetchall()
    assert post_records == 2581934, "Count of records  2581934"
    return post_df


    


# In[ ]:





# In[ ]:




