# SuperPower-API

SuperPower is a real-time mobile strategy game that can be played online with other players

- This is backend part of my mobile online game
- This project is in development

# API Informations

- API is developed using Flask RESTFUL with Python language
- API is used as gateway between Unity Game and SQL Server, also manages some time dependent events too

## Methods ##

Theese methods can be requested from server:

Method | URL 
--- | --- 
GET | /test
POST | /test
POST | /userLogin
POST | /userRegister
POST | /forgotPassword
POST | /countriesDetails
POST | /provincesDetails
POST | /myCountryDetails
POST | /armyInformations
POST | /giveMissionToCorps
POST | /abortMissionOfCorp
POST | /aggrementsInformations
POST | /declineAggrement
POST | /offerAggrement
POST | /answerAggrementOffer
POST | /aggrementOfferInformations
POST | /regulationsInformations
POST | /lawsInformations
POST | /declineRegulation
POST | /declineLaw
POST | /makeRegulation
POST | /makeLaw
POST | /budgetInformations
POST | /setBudgetForProvince
POST | /setBudgetForArmy
POST | /setTaxRateForProvince
POST | /makeInvestment


## What's New ##

- SQL Library changed from pyodbc to pymssql
- Project is moved from Heroku to AWS Elastic Beanstalk
- Only userCheck method is active for now (2/15/2019)


### TODOs: ###

- Make tests for disabled methods and publish
- Make use of DailyUpdates
- Update this readme



### Steps To Deploy: ###

This part is for author, aliihsank to not to forget what to do

1)Make local unit test for every new functionality

1)Check requirements.txt for missing libraries

2)Deploy to remote

3)Make remote unit test from Postman

4)Publish API to public

5)Remove added functionalities from TODO list




