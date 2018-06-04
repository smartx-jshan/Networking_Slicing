#!/bin/bash


ONOS=`cat init | grep ONOS_IP | cut -d '=' -f2`
OpenStack=`cat init | grep OpenStack_Interface | cut -d '=' -f2`


if [ "$ONOS" == "" ]; then
	echo "You should write your ONOS_IP into \"init\""
        exit
fi

if [ "$OpenStack" == "" ]; then
        echo "You should write your OpenStack Interface \"init\""
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


Interfaces=`cat init | grep IoT_Interfaces | cut -d '=' -f2 | tr -d ','`

for i in $Interfaces; do
  ovs-vsctl add-port br-IoT $i
done


Bridges=`cat init | grep IoT_linux_bridges | cut -d '=' -f2 | tr -d ','`

for i in $Bridges; do
  ip link add name veth1_$i type veth peer name veth2_$i
  ifconfig veth1_$i up && ifconfig veth2_$i up
  brctl addif $i veth1_$i
  ovs-vsctl add-port br-IoT veth2_$i
done




