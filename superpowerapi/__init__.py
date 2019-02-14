import os
from flask import Flask, request
from flask_cors import CORS
from flask_restful import Resource, Api

app = Flask(__name__)
app.debug = False
api = Api(app)
CORS(app)

ODBC_URL = os.environ.get('ODBC_URL')

import superpowerapi.spapi
