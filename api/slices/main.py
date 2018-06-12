from flask import Flask, request
from flask_restful import Resource, Api
from flask_restful import reqparse
from flaskext.mysql import MySQL
import subprocess
import json
import requests

app = Flask(__name__)
api = Api(app)


#get the MySQL HOST from init.conf
Host = subprocess.check_output("cat ../configuration/init.conf | grep MySQL_HOST | awk '{print $3}'", shell = True)
Host = Host.decode('UTF-8').strip()

#get the MySQL PASS from init.conf
Pass = subprocess.check_output("cat ../configuration/init.conf | grep MySQL_PASS | awk '{print $3}'", shell = True)
Pass = Pass.decode('UTF-8').strip()

#get the ONOS_IP from init.conf
ONOS = subprocess.check_output("cat ../configuration/init.conf | grep ONOS | awk '{print $3}'", shell = True)
ONOS = ONOS.decode('UTF-8').strip()

#get the OpenStack Interface from init.conf
OpenStack = subprocess.check_output("cat ../configuration/init.conf | grep OpenStack_Interface | awk '{print $3}'", shell = True)
OpenStack = OpenStack.decode('UTF-8').strip()


# FInd DPID of br-vlan from ovs-vsctl command
dpid = subprocess.check_output("ovs-vsctl get bridge br-vlan datapath_id", shell = True)
dpid = dpid.decode('UTF-8').strip()
dpid = dpid.replace("\"", "")


# get the port information from ONOS API
url = "http://" + ONOS + ":8181/onos/v1/devices/of:" + dpid +"/ports"
response = requests.get(url, auth=('karaf', 'karaf'))
data = response.text
output = json.loads(data)


# Find port number
for port in output['ports']:
  if port['annotations']['portName'] == OpenStack:
    Cloud_Interface = port['port']
  if port['annotations']['portName'] == 'slicing_patch1':
    IoT_Interface = port['port']



mysql = MySQL()

# MySQL Config
app.config['MYSQL_DATABASE_USER'] ='slices'
app.config['MYSQL_DATABASE_PASSWORD'] = Pass
app.config['MYSQL_DATABASE_DB'] = 'slices'
app.config['MYSQL_DATABASE_HOST'] = Host

mysql.init_app(app)


@app.route('/')
def Slices():

  return (IoT_Interface)
  #return "Network Slicing v0.1"

@app.route('/slices')
def show_slices():

  # JSON 
  #  slices_id = request.get_json()["Slice_ID"]
  #  MAC = request.get_json()["MAC"]


  cur = mysql.connect().cursor()
  cur.execute("select * from slices")

  result = []

  columns = tuple( [d[0] for d in cur.description])
 
  for row in cur:
    result.append(dict(zip(columns, row)))

  print(result)

  return json.dumps(result)


@app.route('/slices', methods=['POST'])
def create_slices():

  slices = request.get_json()["Slice_ID"]
  mac = request.get_json()["MAC"]
  of_dpid = "of:" + dpid 


  # Check if you already have same slices 
  con = mysql.connect()
  cur = con.cursor()
  para = "select * from slices where MAC='" + mac + "'"
  cur.execute(para)
  
  flag = 0
  for row in cur:
    flag = flag + 1

  if (flag != 0):
    return ("Error: Same slice existed!\n")


  # Check cloud_slice is existed
  para = "select * from cloud_slices where Slice='" + slices + "'"
  cur.execute(para)

  flag = 0
  for row in cur:
    flag = flag + 1

  if (flag == 0):
    # we need to create cloud_slice
    data = {
   "type": "PointToPointIntent",
   "appId": "org.onosproject.cli",
   "priority": 40100,
   "selector":
    {
      "criteria":
      [
        {"type": "VLAN_VID",
         "vlanId": slices
        }
      ]
    },
   "treatment":
     {
      "instructions":
      [
        {"type": "L2MODIFICATION",
         "subtype": "VLAN_POP"
        }
      ]
     },
   "ingressPoint":
     {
      "device": of_dpid,
      "port": Cloud_Interface
     },
   "egressPoint":
     {"device": of_dpid,
      "port": IoT_Interface
     }
    }

    # get url
    url = "http://" + ONOS + ":8181/onos/v1/intents"

    # request POST method
    res = requests.post(url, data =json.dumps(data), auth=('karaf', 'karaf'))

    # get the Intent key
    intent_key = res.headers['location']
    url_app = url + "/org.onosproject.cli/"
    intent_key = intent_key.replace(url_app, "")
    

    # Save information to MySQL
    cmd = "insert into cloud_slices values('" + slices + "', '" + intent_key + "')"
    cur.execute(cmd)
    con.commit()



  # Call ONOS API data
  data = { "type": "PointToPointIntent",
   "appId": "org.onosproject.cli",
   "priority": 40100,
   "selector":
    {
      "criteria":
      [
        {"mac": mac,
         "type": "ETH_SRC"
        }
      ]
    },
   "treatment":
     {
      "instructions":
      [
        {"type": "L2MODIFICATION",
         "subtype": "VLAN_PUSH"
        },
        {"type": "L2MODIFICATION",
         "subtype": "VLAN_ID",
         "vlanId": slices
        }
      ]
     },
   "ingressPoint":
     {
      "device": of_dpid,
      "port": IoT_Interface
     },
   "egressPoint":
     {"device": of_dpid,
      "port": Cloud_Interface
     }}

  # get url
  url = "http://" + ONOS + ":8181/onos/v1/intents"

  # request POST method
  res = requests.post(url, data =json.dumps(data), auth=('karaf', 'karaf'))

  # get the Intent key
  intent_key = res.headers['location']
  url_app = url + "/org.onosproject.cli/"
  intent_key = intent_key.replace(url_app, "")


  # Save information to MySQL

  cmd = "insert into slices values('" + mac + "', '" + slices + "', '" + intent_key + "')"

  #  con = mysql.connect()
  #  cur = con.cursor()
  cur.execute(cmd)
  con.commit()

 
  # return
 
  return (intent_key)




@app.route('/slices', methods=['DELETE'])
def delete_slices():

  # get the mac address and slices
  mac =request.get_json()["MAC"]
  slices = request.get_json()["Slice_ID"]


  # find MYSQL tuple
  con = mysql.connect()
  cur = con.cursor()
  para = "select * from slices where MAC='" + mac + "'"
  cur.execute(para)

  flag = 0
  for row in cur:
    flag = flag + 1

  if (flag == 0):
    return ("Error: slice does not existed!\n")

  # find intent_key
  intent_key = str(row[2])
    

  # get url
  url = "http://" + ONOS + ":8181/onos/v1/intents/org.onosproject.cli/" + intent_key

  # request POST method
  res = requests.delete(url, auth=('karaf', 'karaf'))


  # Delete MySQL tuple
  cmd = "delete from slices where MAC ='" + mac +"'" 
  cur.execute(cmd)
  con.commit()

  # Delete Intent of ONOS
    


  # find another slice with same id
  para = "select * from slices where Slice='" + slices + "'"
  cur.execute(para)
  
  flag = 0
  for row in cur:
    flag = flag + 1

  if (flag == 0):
    # we need to delete cloud_slice
    para = "select * from cloud_slices where Slice='" + slices + "'"
    cur.execute(para)

    for row in cur:
      flag = 0

    intent_key = str(row[1])

    # get url
    url = "http://" + ONOS + ":8181/onos/v1/intents/org.onosproject.cli/" + intent_key

    # request POST method
    res = requests.delete(url, auth=('karaf', 'karaf'))

    # delete mysql
    cmd = "delete from cloud_slices where Slice ='" + slices +"'"
    cur.execute(cmd)
    con.commit()



  return (intent_key)

