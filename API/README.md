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
