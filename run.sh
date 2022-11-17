#!/bin/bash

today=$(date +"%y%m%d")
hour=$(date +"%H%M")
data_time="${today}_${hour}"
home_dir="./data/${today}/${today}_${hour}"

# make folder structure
sudo mkdir -p $home_dir/defender_output/snort_output $home_dir/attacker_output/traces

#configs
# topology_file=

# run testbed
# xterm -hold -e "sudo -E python ./testbed/testbed_topo_TCP_v3.py" &  

# start snort
# sudo snort -A console -c /etc/snort/snort.conf -i attacker-eth0 -h 10.0.0.100/16 -l $home_dir/defender_output/snort_output -A fast & > $home_dir/defender_output/snort_output/console_output.txt &
sudo snort  -c /etc/snort/snort.conf -i attacker-eth0 -h 10.0.0.100/16 -l $home_dir/defender_output/snort_output -A fast &

# run mtd notify
sudo sh ./mod_mtd_notify.sh &> $home_dir/defender_output/mtd_times_$data_time.txt  &
 
# run wireshark
sudo dumpcap -b filesize:100000 -b files:100 -i "attacker-eth0" -w $home_dir/attacker_output/traces -q &

# run data taking script
sudo python ./attacker_script.py $home_dir/attacker_output/ "dig" "/24" "300sMTD, topo_v3, snort rules: default+community,"