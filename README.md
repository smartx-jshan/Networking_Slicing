# Networking_Slicing
Networkig Slicing is RESTful API to provide point to point connection beetween IoT devices and Cloud.

## Requirement
* IoT-Cloud Hub (Speacially prepared hardware for IoT Gateway)
* OpenStack Cloud with VLAN based tenant Network
* Ubuntu 16.04

## Install 

In this step, you should run following commands on IoT-Cloud hub.

```
$ git clone http://github.com/smartx-jshan/networking_slicing
$ cd networking_slicing/installation
```
Install ONOS SDN Controller & OpenvSwtich
```
$ ./install.sh
```
If you don't have MySQL
```
$ ./mysql.sh
```
To run the ONOS Application on background process
```
$ ./ONOS_app.sh
```

## Configuration
Before configuration, you should configure your several Parameters (MYSQL host, password, ONOS host, interfaces, and so on) in init.conf
```
$ cd networking_slicing/configuration
$ vim init.conf 
```
To create DB tables
```
$ ./init_db.sh
```
To create virtual switches and configure interfaces
```
$ ./init_vswitch.sh
```
To activate ONOS applications
```
$ ./ONOS_app.sh
```


## Running API
```
$ cd networking_slicing/api
$ pipenv install
$ ./bootstrap.sh
```

## API Example
It provides basic functionalities for network slicing (Create, Delete and get)

### Create
```
$ curl –X POST –H “Content-Type: application/json” -d ‘{“MAC”: “value”, “Slice_ID”: “value”}’ http://IP:6126/slices
```
### Delete
```
$ curl –X DELETE –H “Content-Type: application/json” -d ‘{“MAC”: “value”, “Slice_ID”: “value”}’ http://IP:6126/slices
```
### Get
```
$ curl http://IP:6126/slices
```





