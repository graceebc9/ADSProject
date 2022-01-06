# ADSProject
Project is structure using the Access, Assess and Address data structure 
1. Price data loaded from web 
2. Postcode data loaded from local file 
3. Extra feature for modelling: POI calculated for each test data lat/lon using OSM API

Shortcomings of the project: 
1. Pulling the Points of Interest takes a long time (~5 minutes per lat/lon) - these are cached when run locally which then speeds up future runs 
2. Project was set up using AWS and accidentally went over the free tier limits, leading to databases needing deletion in order to refund charges 

Other builds on the project are as follows: 
1. Refactor pulling POI to speed up process- I was not able to find a bulk way to calculate POI but would explore how moving up a level of granulaity affected predictions, with the thought being to create a master table at postcode sector to pull from rather than calculating each individual lat/lon 
2.  Explore other features with different combinations of Points of Interests and explore how they correlate with prediction of price 
