#!/bin/sh

HOOK_FILE=/etc/bind/zones/ports.txt

while inotifywait -qq  $HOOK_FILE
do
        echo "Port changed, $(date +'%a %d %b %Y %T.%5N %Z')" | tr '\n' ',';
        cat $HOOK_FILE
done
