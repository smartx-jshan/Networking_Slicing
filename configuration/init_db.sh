#!/bin/bash


# CREATE TABLE

HOST=`cat init.conf | grep MySQL_HOST | awk '{print $3}'`
PASS=`cat init.conf | grep MySQL_PASS | awk '{print $3}'`


if [ "$HOST" == "" ]; then
        echo "You should write your MySQL HOST into \"init.conf\""
        exit
fi

if [ "$PASS" == "" ]; then
        echo "You should write your MySQL Password into \"init.conf\""
        exit
fi

# CREATE Two Table
# slice / cloud_slice

cat << EOF | mysql -uroot -h$HOST -p$PASS
CREATE DATABASE slices;
GRANT ALL PRIVILEGES ON slices.* TO 'slices'@'localhost' IDENTIFIED BY '$PASS';
GRANT ALL PRIVILEGES ON slices.* TO 'slices'@'%' IDENTIFIED BY '$PASS';
use slices;
CREATE TABLE slices(
MAC VARCHAR(30) NOT NULL,
Slice VARCHAR(10) Not NULL,
Intent VARCHAR(10) Not NULL,
PRIMARY KEY (MAC));
CREATE TABLE cloud_slices(
Slice VARCHAR (10) Not NULL,
Intent VARCHAR(10) Not NULL,
PRIMARY KEY (Slice));
quit
EOF

