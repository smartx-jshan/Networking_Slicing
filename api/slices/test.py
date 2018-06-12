from flask import Flask
from flask_restful import Resource, Api
from flask_restful import reqparse
from flaskext.mysql import MySQL
import subprocess

app = Flask(__name__)
api = Api(app)

class CreateSlices(Resource):
  def post(self):
    try:
      parser = reqparse.RequestParser()
      parser.add_argument('Slice_ID', type=str)
      parser.add_argument('MAC', type=str)
      args = parser.parse_args()


      conn = mysql.connect()
      cursor = conn.cursor()
      cursor.callproc(

      _ID = args['Slice_ID']
      _MAC = args['MAC']
      
      if _ID == None or _MAC == None:
        return {'Error': 'Arguments are not valid'}
      else:

        #save information to MYSQL
        
        #get the mysql address
        Host = subprocess.check_output("cat ../configuration/init.conf | grep MySQL | awk '{print $3}'", shell = True)
        Host = Host.decode('UTF-8').strip()

         
        return {'Slice_ID': args['Slice_ID'], 'MAC': args['MAC'], 'host': Host}
    
    except Exception as e:
      return {'error': str(e)}


api.add_resource(CreateSlices, '/slices')





#@app.route("/")
#def hello_world():
#  return "Hello, World!"

