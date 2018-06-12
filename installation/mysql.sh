#!/bin/bash

if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi




Bind_Address="localhost"
PASSWORD="localhost"



# Install & Configure MYSQL

sudo debconf-set-selections <<< "mariadb-server mysql-server/root_password password $PASSWORD"
sudo debconf-set-selections <<< "mariadb-server mysql-server/root_password_again password $PASSWORD"
sudo apt-get -y install mariadb-server python-pymysql

sudo touch /etc/mysql/mariadb.conf.d/99-slicing.cnf

echo "[mysqld]" >> /etc/mysql/mariadb.conf.d/99-slicing.cnf
echo "bind-address = $Bind_Address" >> /etc/mysql/mariadb.conf.d/99-slicing.cnf
echo "default-storage-engine = innodb" >> /etc/mysql/mariadb.conf.d/99-slicing.cnf
echo "innodb_file_per_table = on" >> /etc/mysql/mariadb.conf.d/99-slicing.cnf
echo "max_connections  = 4096" >> /etc/mysql/mariadb.conf.d/99-slicing.cnf
echo "collation-server = utf8_general_ci" >> /etc/mysql/mariadb.conf.d/99-slicing.cnf
echo "character-set-server = utf8" >> /etc/mysql/mariadb.conf.d/99-slicing.cnf

service mysql restart

echo -e "$PASSWORD\nn\ny\ny\ny\ny" | mysql_secure_installation

