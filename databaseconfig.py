#!/usr/bin/env python
# coding: utf-8

# In[8]:


import mysql.connector
from pathlib import Path
from dotenv import load_dotenv
import os


# In[9]:


# load passwords 
dotenv_path = Path('/Users/gracecolverd/config.env')
load_dotenv(dotenv_path=dotenv_path)

USR = os.getenv("USR")
PASSWORD = os.getenv("PASSWORD")


# In[10]:



ENDPOINT="db3.csxdtoznyujn.eu-west-2.rds.amazonaws.com"
PORT="3306"
REGION="eu-west-2b"
DBNAME="property_prices"


connection =   mysql.connector.connect( user=USR, password=PASSWORD, database=DBNAME,  host=ENDPOINT , port =PORT, allow_local_infile = True, autocommit = True)
cursor = connection.cursor()

if (connection.is_connected()):
    print("Connected")
else:
    print("Not connected")


# In[11]:



mysql = {
    "host": ENDPOINT,
    "user": USR,
    "passwd": PASSWORD,
    "db": DBNAME,
}







