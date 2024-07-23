#!/bin/sh

HOOK_FILE=/etc/bind/zones/forward.mj.uq.dslab.com.db

while inotifywait -qq  $HOOK_FILE
do
        echo "IP changed, at $(date +'%a %d %b %Y %T.%5N %Z')" | tr '\n' ',';
        cat $HOOK_FILE | grep "www"
        sudo rndc reload mj.uq.dslab.com
done
