#!/bin/bash


echo -n "ONOS IP: "
read ONOS_IP


# Activate OpenFlow
curl -X POST  "http://$ONOS_IP:8181/onos/v1/applications/org.onosproject.openflow/active" --user karaf:karaf

# Activate Reactive Forwarding
curl -X POST  "http://$ONOS_IP:8181/onos/v1/applications/org.onosproject.fwd/active" --user karaf:karaf


