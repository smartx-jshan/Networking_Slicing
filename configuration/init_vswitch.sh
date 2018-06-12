#!/bin/bash


ONOS=`cat init.conf | grep ONOS_IP | awk '{print $3}'`
OpenStack=`cat init.conf | grep OpenStack_Interface | awk '{print $3}'`


if [ "$ONOS" == "" ]; then
	echo "You should write your ONOS_IP into \"init.conf\""
        exit
fi

if [ "$OpenStack" == "" ]; then
        echo "You should write your OpenStack Interface into \"init.conf\""
        exit
fi



# add bridge
ovs-vsctl add-br br-vlan
ovs-vsctl add-br br-IoT

#set controller
ovs-vsctl set-controller br-vlan tcp:$ONOS:6633
ovs-vsctl set-controller br-IoT tcp:$ONOS:6633

#connection between two brdiges
ovs-vsctl add-port br-vlan slicing_patch1 -- set interface slicing_patch1 type=patch options:peer=slicing_patch0
ovs-vsctl add-port br-IoT slicing_patch0 -- set interface slicing_patch0 type=patch options:peer=slicing_patch1


# add port
ovs-vsctl add-port br-vlan $OpenStack


# Add IoT Interfaces
Interfaces=`cat init.conf | grep IoT_Interfaces | cut -d '=' -f2 | tr -d ','`

for i in $Interfaces; do
  ovs-vsctl add-port br-IoT $i
done


# Add linux bridges
Bridges=`cat init.conf | grep IoT_linux_bridges | cut -d '=' -f2 | tr -d ','`

for i in $Bridges; do
  ip link add name veth1_$i type veth peer name veth2_$i
  ifconfig veth1_$i up && ifconfig veth2_$i up
  brctl addif $i veth1_$i
  ovs-vsctl add-port br-IoT veth2_$i
done




