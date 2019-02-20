#DEFINITIONS
"""
INFO 1= Successful request, 0 or -1 = Server or Database Error
DETAILS RETURN VALUE: (real return value that user is waiting)

"""


import os
from collections import defaultdict
from threading import Thread
import schedule
import datetime
import time

from flask import Flask, request
from flask_cors import CORS
from flask_restful import Resource, Api

import pymssql

application = Flask(__name__)
#application.debug = False
api = Api(application)
CORS(application)


RDS_SERVER_NAME = 'aa1ddkx4hgbroia.ciwdqj6fxzhj.eu-central-1.rds.amazonaws.com:1433'#os.environ.get('RDS_SERVER_NAME')
RDS_DATABASE = 'superpower'#os.environ.get('RDS_DATABASE')
RDS_USER = 'admin'#os.environ.get('RDS_USER')
RDS_PASSWORD = 'ninjaminja'#os.environ.get('RDS_PASSWORD')



########## UTIL METHODS ##############

#SEALED
def DailyUpdateInParallel():
    schedule.every().day.at("11:20").do(DailyUpdateMethod)

    while 1:
        schedule.run_pending()
        time.sleep(1)
        

#SEALED
def DailyUpdateMethod():
    # This pseude-code is for daily resource increase-decrease and population change check '''
    # Also there is tax control method in sql server as Stored Procedure '''
            
    #Get country id's from country table , foreach it      COUNTRY
                
        #Define restFoodDecrease = 0
        #Define restDrinkDecrease = 0
        #Get province id's from provinces table, foreach it     PROVINCE
                    
            #Su ve yiyecek aynı miktarda tüketileceğinden ikisi de decreaseBesin olarak adlandırıldı.(nüfus kadar)
            #restFoodDecrease += decreaseBesin
            #restDrinkDecrease += decreaseBesin
                    
            #Tüm kaynaklar için
            #Calculate totalKaynak += amount + increaseKaynak      province diğer kaynak değişimleri

            #Get resourceID's from ProvinceResources table, foreach it  RESOURCE - benim resource'larımı döndür
                    
                #if #Check resources from Natural resources data table, if type is drink:   RESOURCE-TYPE-CHECK
                    #amount = amount + increaseBesin
                    #if amount - restDrinkDecrease < 0:
                        #restDrinkDecrease -= amount
                        #amount = 0
                    #else
                        #restDrinkDecrease = 0
                        #amount = amount - restDrinkDecrease
                        
                #if #Check if type is food:
                    #amount = amount + increaseBesin
                    #if amount - restFoodDecrease < 0:
                        #restFoodDecrease -= amount
                        #amount = 0
                    #else
                        #restFoodDecrease = 0
                        #amount = amount - restFoodDecrease
                        
                #if #Check if type is resource:
                    #amount = totalKaynak
                            
                #SaveMyResourceValue(provinceId, resourceId, amount)
                        
            #if restFoodDecrease > 0 OR restDrinkDecrease > 0:
                #SaveNewPopulation(randomProvinceId, restFoodDecrease>restDrinkDecrease?restFoodDecrease:restDrinkDecrease)
        
        
    try:
        conn = pymssql.connect(server = RDS_SERVER_NAME, user = RDS_USER, password = RDS_PASSWORD, database = RDS_DATABASE, autocommit=True)
        cursor = conn.cursor(as_dict = True)
            
        #FUNCTION PARAMETERS
        increaseResource = 200
        increaseBesin = 7000
        taxDivisor = 100
        besinDivisor = 1000
        ###################
            
        #Pay Taxes to Country every day
        params = (taxDivisor,)
        cursor.callproc('payTaxes', (params))
        if cursor.nextset():
            result = cursor.fetchone()
            if result['Result'] != 1:
                return {'info': 1, 'details': -1}
        else:
            return {'info': 1, 'details': -1}
            
        #Take ProvinceResources table down to update it, daily
        params = ()
        cursor.callproc('returnResourceValues', (params))
        if cursor.nextset():
            result = cursor.fetchall()
        else:
            return {'info': 1, 'details': -1}
            
        #Group provinces according to countries they belong
        groups = defaultdict(list)
        for row in result:
            groups[row['CountryID']].append(row)
            
        countries = groups.values()
            
        update_list = []
            
        #Make Changes on Resources
        for country in countries:
            restFoodDecrease = 0
            restDrinkDecrease = 0
            
            print(country)
            countryID = 0
                
            for provinceXResource in country:
                #print(provinceXResource)
                countryID = provinceXResource['CountryID']
                population = provinceXResource['Population']
                restFoodDecrease += population / besinDivisor
                restDrinkDecrease += population / besinDivisor
                    
                amount = provinceXResource['Amount']
                    
                if provinceXResource['Type'] == 'drink':
                    amount = amount + increaseBesin
                    if amount - restDrinkDecrease < 0:
                        restDrinkDecrease -= amount
                        amount = 0
                    else:
                        restDrinkDecrease = 0
                        amount = amount - restDrinkDecrease
                if provinceXResource['Type'] == 'food':
                    amount = amount + increaseBesin
                    if amount - restFoodDecrease < 0:
                        restFoodDecrease -= amount
                        amount = 0
                    else:
                        restFoodDecrease = 0
                        amount = amount - restFoodDecrease
                if provinceXResource['Type'] == 'resource':
                    amount = amount + increaseResource
                    
                #Add new resource values to local list
                update_list.append((amount, provinceXResource['ProvinceID'], provinceXResource['ResourceID']))
                    
            if restFoodDecrease > 0 or restDrinkDecrease > 0:
                num_of_deads = restFoodDecrease if restFoodDecrease > restDrinkDecrease else restDrinkDecrease
                
                params = (num_of_deads, countryID, countryID,)
                #Kill equal # of people in every province of same country
                cursor.execute("""UPDATE P 
                                SET P.population = P.population - (%d / (select count(*) from Province K where K.countryID = %d and K.population > 0))
                                FROM dbo.Province AS P
                                where P.countryID = %d and P.population > 0""", params)
                    
        #Update ProvinceResources with new values
        cursor.executemany('update dbo.ProvinceResources set amount = %d where provinceID = %d and resourceID = %d', update_list)
        
        print("Daily Update Finished Successfuly!")
    except Exception as e:
        print("Error in Daily Update: " + str(e))


######## API RESOURCE CLASSES ########

#SEALED
class MainPage(Resource):
    def get(self):
        return {"Author": "Ali İhsan KARABAL", "Project Name": "Super Power API", "Definition": "Mobile Game API", "Server Time": str(datetime.datetime.now())}

#SEALED
class Test(Resource):
    def get(self):
        return {'Test Message(GET)': 'Welcome to new API !!'}
    
    def post(self):
        return {'Test Message(POST)': 'Welcome to new API !!'}

#SEALED
class DailyUpdate(Resource):    
    def post(self):
        
        run = Thread(target = DailyUpdateInParallel , args = ())
        run.start()
        return {'info': 1, 'details': 'Daily Update Started in different thread!'}
        

#SEALED
#Takes : email, password
#Returns : uid
class UserLogin(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']
        
        try:
            conn = pymssql.connect(server = RDS_SERVER_NAME, user = RDS_USER, password = RDS_PASSWORD, database = RDS_DATABASE, autocommit=True)
            cursor = conn.cursor(as_dict = True)
                        
            params = (email, password,)
            cursor.callproc('userLogin', (params))
            if cursor.nextset():
                result = cursor.fetchone()
                cursor.close()
                conn.close()
                return {'info': 1, 'details': result['ID']}
            else:
                cursor.close()
                conn.close()
                return {'info': 1, 'details': -1}
        except Exception as e:
            print("Error: " + str(e))
            return {'info': -1, 'details': str(e)}

#SEALED
#Takes : uname, cname, email, password
#Returns : Result as (1,0,-1)
class UserRegister(Resource):
    def post(self):
        data = request.get_json()
        uname = data['uname']
        countryName = data['cname']
        email = data['email']
        password = data['password']
                
        try:
            conn = pymssql.connect(server = RDS_SERVER_NAME, user = RDS_USER, password = RDS_PASSWORD, database = RDS_DATABASE, autocommit = True)
            cursor = conn.cursor(as_dict = True)
            
            params = (uname, countryName, email, password,)
            cursor.callproc('userRegister', (params))
            if cursor.nextset():
                result = cursor.fetchone()
                
                if 'id' in result:
                    cursor.nextset()
                    result = cursor.fetchone()
                
                return {'info': 1, 'details': result['Result']}
            else:
                return {'info': 0, 'details': 'An Error Occured!'}
        except Exception as e:
            print("Error: " + str(e))
            return {'info': -1, 'details': str(e)}

#SEALED
#Takes : email, password
#Returns : cid, cname, totalPopulation, avgTaxRate, #ofProvinces, remainingOfIncome
class MyCountryDetails(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']        
                
        try:
            conn = pymssql.connect(server = RDS_SERVER_NAME, user = RDS_USER, password = RDS_PASSWORD, database = RDS_DATABASE, autocommit = True)
            cursor = conn.cursor(as_dict = True)
                        
            params = (email, password,)
            cursor.callproc('myCountryDetails', (params))
            if cursor.nextset():
                result = cursor.fetchone()
        
                return {'info': 1, 'details': result}
            else:
                return {'info': 0, 'details': 'An Error Occured!'}
        except Exception as e:
            print("Error: " + str(e))
            return {'info': -1, 'details': str(e)}


#SEALED
#Takes : email, password
#Returns : cid, cname, totalPopulation, avgTaxRate, #ofProvinces, statusWith(me)
class OtherCountriesDetails(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']
     
        try:
            conn = pymssql.connect(server = RDS_SERVER_NAME, user = RDS_USER, password = RDS_PASSWORD, database = RDS_DATABASE, autocommit = True)
            cursor = conn.cursor(as_dict = True)
                
            params = (email, password,)
            cursor.callproc('otherCountriesDetails', (params))
            if cursor.nextset():
                result = cursor.fetchall()
        
                return {'info': 1, 'details': result}
            else:
                return {'info': 0, 'details': 'An Error Occured!'}
        except Exception as e:
            print("Error: " + str(e))
            return {'info': -1, 'details': str(e)}


#SEALED
#Params : email, password
#Returns : pid, pname, governorName, population, taxRate 
class MyProvincesDetails(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']
        
        try:
            conn = pymssql.connect(server = RDS_SERVER_NAME, user = RDS_USER, password = RDS_PASSWORD, database = RDS_DATABASE, autocommit = True)
            cursor = conn.cursor(as_dict = True)
                        
            params = (email, password,)
            cursor.callproc('myProvincesDetails', (params))
            if cursor.nextset():
                result = cursor.fetchall()
        
                return {'info': 1, 'details': result}
            else:
                return {'info': 0, 'details': 'An Error Occured!'}
        except Exception as e:
            print("Error: " + str(e))
            return {'info': -1, 'details': str(e)}
        
        

#SEALED
#Params : email, password
#Returns : pid, pname, population, governorName
class OtherProvincesDetails(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']
        
        try:
            conn = pymssql.connect(server = RDS_SERVER_NAME, user = RDS_USER, password = RDS_PASSWORD, database = RDS_DATABASE, autocommit = True)
            cursor = conn.cursor(as_dict = True)
            
            params = (email, password,)
            cursor.callproc('otherProvincesDetails', (params))
            if cursor.nextset():
                result = cursor.fetchall()
    
                return {'info': 1, 'details': result}
            else:
                return {'info': 0, 'details': 'An Error Occured!'}
        except Exception as e:
            print("Error: " + str(e))
            return {'info': -1, 'details': str(e)}


'''
#Returns : My army informations - armyBudget, List<armyCorps,opearation>
class ArmyInformations(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']
        countryID = data['countryId']
        
        rows = cursor.execute("{call armyInformations(?,?,?)}", (email, password, countryID)).fetchall()
        dataList = []
        for row in rows:
            data_as_dict = {
                "id" : row[0],
                "budget" : row[1],
                "corpDetails" : row[2]
                }
            dataList.append(data_as_dict)
            
        return json.dumps(dataList)

#Params : corpId, targetProvinceId, mission
#Returns : successful
class GiveMissionToCorps(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']
        corpID = ['corpId']
        provinceID = ['provinceId']
        mission = ['mission']
            
        
        success = cursor.execute("{call giveMissionToCorps(?,?,?,?,?)}", (email, password, corpID, provinceID, mission)).fetchval()
        if(success >= 0):
            return {'successful': True}
        else:
            return {'successful': False}
        
        
#Params : corpId,missionId
#Returns : successful
#Definition : Gives corps a new mission about going back to where they came
class AbortMissionOfCorp(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']
        corpID = ['corpId']
        missionID = ['missionId']

        success = cursor.execute("{call abortMissionOfCorp(?,?,?,?)}", (email, password, corpID, missionID)).fetchval()
        if(success >= 0):
            return {'successful': True}
        else:
            return {'successful': False}
        

#Returns : rows in countryAggrements table related to users country
class AggrementsInformations(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']
        countryID = data['countryId']

        rows = cursor.execute("{call aggrementsInformations(?,?,?)}", (email, password, countryID)).fetchall()
        dataList = []
        for row in rows:
            data_as_dict = {
                "c1Id" : row[0],
                "c2Id" : row[1],
                "aggrementId" : row[2],
                "endDate": row[3]
                }
            dataList.append(data_as_dict)
            
        return json.dumps(dataList)
        
    
#Params : c1Id, c2Id, aggrementId
#Returns : successful
class DeclineAggrement(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']
        c1ID = data['c1Id']
        c2ID = data['c2Id']
        aggrementID = data['aggrementId']

        success = cursor.execute("{call declineAggrement(?,?,?,?,?)}", (email, password, c1ID, c2ID, aggrementID)).fetchval()
        if(success >= 0):
            return {'successful': True}
        else:
            return {'successful': False}
        

#Params : c1Id, c2Id, aggrementId, endDate
#Returns : successful
class OfferAggrement(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']
        c1ID = data['c1Id']
        c2ID = data['c2Id']
        aggrementID = data['aggrementId']
        endDate = data['endDate']

        success = cursor.execute("{call offerAggrement(?,?,?,?,?,?)}", (email, password, c1ID, c2ID, aggrementID, endDate)).fetchval()
        if(success >= 0):
            return {'successful': True}
        else:
            return {'successful': False}
        

#Params : c1Id, c2Id, aggrementId, answer
#Returns : successful
class AnswerAggrementOffer(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']
        c1ID = data['c1Id']
        c2ID = data['c2Id']
        aggrementID = data['aggrementId']
        endDate = data['endDate']
        answer = data['answer']

        success = cursor.execute("{call answerAggrementOffer(?,?,?,?,?,?,?)}", (email, password, c1ID, c2ID, aggrementID, endDate, answer)).fetchval()
        if(success >= 0):
            return {'successful': True}
        else:
            return {'successful': False}
    
#Returns : rows in aggrementOffers table related to users country
class AggrementOfferInformations(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']
        countryID = data['countryId']

        rows = cursor.execute("{call aggrementOfferInformations(?,?,?)}", (email, password, countryID)).fetchall()
        dataList = []
        for row in rows:
            data_as_dict = {
                "c1Id" : row[0],
                "c2Id" : row[1],
                "aggrementId" : row[2],
                "endDate": row[3]
                }
            dataList.append(data_as_dict)
            
        return json.dumps(dataList)
    
    
#Returns : rows in countryRegulations table related to users country
class RegulationsInformations(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']
        countryID = data['countryId']

        rows = cursor.execute("{call regulationsInformations(?,?,?)}", (email, password, countryID)).fetchall()
        dataList = []
        for row in rows:
            data_as_dict = {
                "rId" : row[1],
                "startDate" : row[2],
                "endDate" : row[3]
                }
            dataList.append(data_as_dict)
            
        return json.dumps(dataList)
    
    
#Returns : rows in countryLaws table related to users country
class LawsInformations(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']
        countryID = data['countryId']

        rows = cursor.execute("{call lawsInformations(?,?,?)}", (email, password, countryID)).fetchall()
        dataList = []
        for row in rows:
            data_as_dict = {
                "rId" : row[1],
                "startDate" : row[2],
                "endDate" : row[3]
                }
            dataList.append(data_as_dict)
            
        return json.dumps(dataList)
    
    
#Params : cId, rId
#Returns : successful
class DeclineRegulation(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']
        countryID = data['countryId']
        regulationID = data['regulationId']

        success = cursor.execute("{call declineRegulation(?,?,?,?)}", (email, password, countryID, regulationID)).fetchval()
        if(success >= 0):
            return {'successful': True}
        else:
            return {'successful': False}
        
    
#Params : cId, lId
#Returns : successful
class DeclineLaw(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']
        countryID = data['countryId']
        lawID = data['lawId']

        success = cursor.execute("{call declineLaw(?,?,?,?)}", (email, password, countryID, lawID)).fetchval()
        if(success >= 0):
            return {'successful': True}
        else:
            return {'successful': False}


#Params : cId, rId, endDate
#Returns : successful
class MakeRegulation(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']
        countryID = data['countryId']
        regulationID = data['regulationId']
        endDate = data['endDate']

        success = cursor.execute("{call makeRegulation(?,?,?,?,?)}", (email, password, countryID, regulationID, endDate)).fetchval()
        if(success >= 0):
            return {'successful': True}
        else:
            return {'successful': False}
    
#Params : cId, lId
#Returns : successful
class MakeLaw(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']

        countryID = data['countryId']
        lawID = data['lawId']
        endDate = data['endDate']

        success = cursor.execute("{call makeLaw(?,?,?,?,?)}", (email, password, countryID, lawID, endDate)).fetchval()
        if(success >= 0):
            return {'successful': True}
        else:
            return {'successful': False}
        
    
#Returns : users provinces last bugdets
class BudgetInformations(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']
        countryID = data['countryId']

        rows = cursor.execute("{call budgetInformations(?,?,?)}", (email, password, countryID)).fetchall()
        dataList = []
        for row in rows:
            data_as_dict = {
                "provinceID" : row[0],
                "amount" : row[1],
                "remaining" : row[2],
                "year" : row[3]
                }
            dataList.append(data_as_dict)
            
        return json.dumps(dataList)
    
    
#Params : provinceId, amount, year
#Returns : successful
class SetBudgetForProvince(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']
        provinceID = ['provinceId']
        year = data['year']
        amount = data['amount']

        success = cursor.execute("{call setBudgetForProvince(?,?,?,?,?)}", (email, password, provinceID, year, amount)).fetchval()
        if(success >= 0):
            return {'successful': True}
        else:
            return {'successful': False}
        
    
#Params : amount
#Returns : successful
class SetBudgetForArmy(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']
        amount = ['amount']
        countryID = data['countryId']

        success = cursor.execute("{call setBudgetForArmy(?,?,?,?,?)}", (email, password, amount, countryID)).fetchval()
        if(success >= 0):
            return {'successful': True}
        else:
            return {'successful': False}
        

#Params : provinceId, taxRate
#Returns : successful
class SetTaxRateForProvince(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']
        provinceID = data['provinceId']
        taxRate = data['taxRate']

        success = cursor.execute("{call setTaxRateForProvince(?,?,?,?)}", (email, password, provinceID, taxRate)).fetchval()
        if(success >= 0):
            return {'successful': True}
        else:
            return {'successful': False}
        
    
#Params : provinceId, investmentId, degree
#Returns : successful
class MakeInvestment(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']
        provinceID = data['provinceId']
        investmentID = data['investmentId']
        degree = data['degree']
        
        success = cursor.execute("{call makeInvestment(?,?,?,?)}", (email, password, provinceID, investmentID, degree)).fetchval()
        if(success >= 0):
            return {'successful': True}
        else:
            return {'successful': False}
        
'''
#######################################
        
api.add_resource(MainPage, '/')
api.add_resource(Test, '/test')

api.add_resource(DailyUpdate, '/dailyUpdate')

api.add_resource(UserLogin, '/userLogin')  

api.add_resource(UserRegister, '/userRegister')

#Forgot Password - Disabled For Now
#api.add_resource(ForgotPassword, '/forgotPassword')

api.add_resource(MyCountryDetails, '/myCountryDetails')
api.add_resource(OtherCountriesDetails, '/otherProvincesDetails')
api.add_resource(MyProvincesDetails, '/myProvincesDetails')
api.add_resource(OtherProvincesDetails, '/otherProvincesDetails')

"""
api.add_resource(ArmyInformations, '/armyInformations')
api.add_resource(GiveMissionToCorps, '/giveMissionToCorps')
api.add_resource(AbortMissionOfCorp, '/abortMissionOfCorp')

api.add_resource(AggrementsInformations, '/aggrementsInformations')
api.add_resource(AggrementOfferInformations, '/aggrementOfferInformations')
api.add_resource(OfferAggrement, '/offerAggrement')
api.add_resource(DeclineAggrement, '/declineAggrement')
api.add_resource(AnswerAggrementOffer, '/answerAggrementOffer')

api.add_resource(RegulationsInformations, '/regulationsInformations')
api.add_resource(LawsInformations, '/lawsInformations')
api.add_resource(DeclineRegulation, '/declineRegulation')
api.add_resource(DeclineLaw, '/declineLaw')
api.add_resource(MakeRegulation, '/makeRegulation')
api.add_resource(MakeLaw, '/makeLaw')

api.add_resource(BudgetInformations, '/budgetInformations')
api.add_resource(SetBudgetForProvince, '/setBudgetForProvince')
api.add_resource(SetBudgetForArmy, '/setBudgetForArmy')
api.add_resource(SetTaxRateForProvince, '/setTaxRateForProvince')

api.add_resource(MakeInvestment, '/makeInvestment')

"""
