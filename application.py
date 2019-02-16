#DEFINITIONS
"""
INFO 1= Successful request, 0 or -1 = Server or Database Error
DETAILS RETURN VALUE: (real return value that user is waiting)

"""


import os
from flask import Flask, request
from flask_cors import CORS
from flask_restful import Resource, Api

import pymssql
import json


application = Flask(__name__)
#application.debug = False
api = Api(application)
CORS(application)


RDS_SERVER_NAME = os.environ.get('RDS_SERVER_NAME')
RDS_DATABASE = os.environ.get('RDS_DATABASE')
RDS_USER = os.environ.get('RDS_USER')
RDS_PASSWORD = os.environ.get('RDS_PASSWORD')


######## API RESOURCE CLASSES ########

class MainPage(Resource):
    def get(self):
        return {"Author": "Ali İhsan KARABAL", "Project Name": "Super Power API", "Definition": "Mobile Game API"}


class Test(Resource):
    def get(self):
        return {'Test Message(GET)': 'Welcome to new API !!'}
    
    def post(self):
        return {'Test Message(POST)': 'Welcome to new API !!'}


#Takes : email, password
#Returns : uid
class UserLogin(Resource):
    def post(self):
        try:
            conn = pymssql.connect(server = RDS_SERVER_NAME, user = RDS_USER, password = RDS_PASSWORD, database = RDS_DATABASE, autocommit=True)
            cursor = conn.cursor(as_dict = True)
            
            data = request.get_json()
            email = data['email']
            password = data['password']
                        
            params = (email, password,)
            cursor.callproc('userLogin', (params))
            if cursor.nextset():
                result = cursor.fetchone()
                return {'info': 1, 'details': result['ID']}
            else:
                return {'info': 1, 'details': -1}
        except Exception as e:
            print("Error: " + str(e))
            return {'info': -1, 'details': str(e)}


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
                            
                if result["Result"] == 1:
                    return {'info': 1, 'details': 1} 
                elif result["Result"] == 0:
                    return {'info': 1, 'details': 0}
                elif result["Result"] == -1:
                    return {'info': 1, 'details': -1}
            else:
                return {'info': 0, 'details': 'An Error Occured!'}
        except Exception as e:
            print("Error: " + str(e))
            return {'info': -1, 'details': str(e)}


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
                result = cursor.fetchone()
        
                return {'info': 1, 'details': result}
            else:
                return {'info': 0, 'details': 'An Error Occured!'}
        except Exception as e:
            print("Error: " + str(e))
            return {'info': -1, 'details': str(e)}


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
            cursor.nextset()
            result = cursor.fetchall()
    
            return {'info': 1, 'details': result}
        except Exception as e:
            print("Error: " + str(e))
            return {'info': -1, 'details': str(e)}
        
        

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
            cursor.nextset()
            result = cursor.fetchall()
    
            return {'info': 1, 'details': result}
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

api.add_resource(UserLogin, '/userLogin')  

api.add_resource(UserRegister, '/userRegister')

#Forgot Password - Disabled For Now
#api.add_resource(ForgotPassword, '/forgotPassword')

api.add_resource(MyCountryDetails, '/myCountriesDetails')
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
