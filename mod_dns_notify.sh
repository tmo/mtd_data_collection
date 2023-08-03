#!/bin/sh

###
# the forward file is also checked instead of sending a dns request so 
# for the dns update just check the update to this file which should
# onlky come from reload.sh which is called by the mtd applicateion
###

HOOK_FILE=/etc/bind/zones/reverse.mj.uq.dslab.com.db

while inotifywait -qq  $HOOK_FILE
do
        echo "IP changed, at $(date -Ins)";

        echo "\n $(date -Ins) sw1" 
        # sudo ovs-ofctl dump-flows s1  --protocols=OpenFlow13 
        echo "\n $(date -Ins) sw2" 
        # sudo ovs-ofctl dump-flows s2  --protocols=OpenFlow13 
done



