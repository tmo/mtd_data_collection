#!/bin/bash
# # Runs complete simulation to take data

today=$(date +"%y%m%d")
hour=$(date +"%H%M")
data_time="${today}_${hour}"
home_dir="./data/${today}/${today}_${hour}"

# export home_dir

# make folder structure
sudo mkdir -p $home_dir/defender_output/snort_output $home_dir/defender_output/traces  $home_dir/attacker_output/traces $home_dir/direct_logs

# copy onos log files before exit
# trap "sudo docker cp onos_new:/root/onos/apache-karaf-4.2.8/data/log/karaf.log $home_dir/direct_logs/karaf.log; exit"  INT TERM
trap  'exit_cmds'  INT TERM

exit_cmds() {
    sudo docker cp onos_new:/root/onos/apache-karaf-4.2.8/data/log/karaf.log $home_dir/direct_logs/karaf.log
    sudo cp /var/log/named/bind.log $home_dir/direct_logs/bind.log
      
    exit
}

# clear bind log so that we only recoord during this
rm /var/log/named/bind.log
sudo systemctl restart bind9

# settings
mtd_file="./mtd_apps/real_drop_cidr16_180_onos-app-mtd-2.4.2.oar"
topology_file="./testbed/testbed_topo_TCP_v6.py"
commit=" "
info="\nClient freq: 13s, Attacker frequency: no attacker\nAim: corrected data aquisition \n Skip DNS "

# write out the reason and settings for this run
echo "\n...\n"$home_dir "\nMTD file: " $mtd_file "\nToplogy file:" $topology_file $commit  $info >> $home_dir/info.txt

# copy server files into correct folder, for default server 1
sudo cp -R ./testbed/server_files/html/. /var/www/html/


# restart bind 9
# sudo systemctl restart bind9 ; named-checkconf ; sudo rndc reload mj.uq.dslab.com

# load ONOS
# remove any previous containers left over (should still pass if there isn't one)
sudo docker stop onos_new
sudo docker rm onos_new
# load container again
echo "Running docker..."
sudo docker run -t -d -v /etc/bind/zones:/etc/bind/zones -p 8101:8101 -p 5005:5005 -p 8181:8181 -p 6653:6653 -p 3000:3000 -p 830:830 --env JAVA_DEBUG_PORT="0.0.0.0:5005" --name onos_new onosproject/onos:2.4.0
echo "Waiting for container to start ..."
sleep 60 # timed, 40 is about right
# start openflow services
echo "Logging in ..."
sudo ssh-keygen -f "/root/.ssh/known_hosts" -R "[172.17.0.2]:8101"
sudo sshpass -p "karaf" ssh -p 8101 karaf@172.17.0.2 -y -o StrictHostKeyChecking=no  'app activate org.onosproject.openflow && logout' 
# sudo sshpass -p "karaf" ssh karaf@172.17.0.1:8101 -y -o StrictHostKeyChecking=no 'app activate org.onosproject.openflow && org.onosproject.fwd && logout'
# copy ans start mtd application
echo "Creating folder..."
sudo docker exec -it onos_new  sh -c  "mkdir /root/onos/conts/ "
echo "Copying mtd file..."
sudo docker cp $mtd_file onos_new:/root/onos/conts/mtd.oar
sleep 20
# sudo docker exec -it onos_new  sh -c "/root/onos/bin/onos-app localhost install! /root/onos/conts/mtd_drop_60.oar"
echo "Finished running onos"

# run mtd inotify, this notifies whenever the IP address of a host changes
sudo killall inotifywait
# sudo sh ./mod_mtd_notify.sh &> $home_dir/defender_output/mtd_times_$data_time.txt &
sudo bash -c "./mod_mtd_notify.sh &>> $home_dir/defender_output/mtd_times_$data_time.txt" &
sudo bash -c "./mod_dns_notify.sh &>> $home_dir/direct_logs/dns_times_$data_time.log" &

# run testbed and scripts for each host
# sudo mn -c && sudo -E python ./testbed/testbed_topo_TCP_v5.py $home_dir $home_dir/defender_output/ $home_dir/attacker_output/ 
sudo killall xterm
sudo -E xterm -hold -e bash -c "sudo mn -c && sudo -E python $topology_file $home_dir $home_dir/defender_output/ $home_dir/attacker_output/ " &

# wait for interfaces to be up
sleep 30
# start snort
# this only tracks the server IPs
sudo bash -c "sudo snort -c /etc/snort/snort.conf -i s1-eth1 -h 10.0.0.100/16 -l $home_dir/defender_output/snort_output -A fast &> $home_dir/direct_logs/snort_dirlog.txt &" &

# might be best to later intentionally name links, but for now can type net to track connections
# run packet capture, on all links from simulated switch 1
sudo dumpcap -b filesize:100000 -b files:100 -i "s1-eth1"  -w $home_dir/attacker_output/traces/trace_s1_eth1 -q &
sudo dumpcap -b filesize:100000 -b files:100 -i "s1-eth2"  -w $home_dir/attacker_output/traces/trace_s1_eth2 -q &
sudo dumpcap -b filesize:100000 -b files:100 -i "s1-eth3"  -w $home_dir/attacker_output/traces/trace_s1_eth3 -q &
# sudo dumpcap -b filesize:100000 -b files:100 -i "s1-eth4"  -w $home_dir/attacker_output/traces/trace_s1_eth4 -q &
# sudo dumpcap -b filesize:100000 -b files:100 -i "s1-eth5"  -w $home_dir/attacker_output/traces/trace_s1_eth5 -q &
sudo dumpcap -b filesize:100000 -b files:100 -i "s1-eth2" -i "s1-eth3"  -w $home_dir/attacker_output/traces/trace_s1_all -q &


# capturing on server for delay tracking
sudo dumpcap -b filesize:100000 -b files:100 -i "s2-eth1"  -w $home_dir/defender_output/traces/trace_s2_eth1 -q &
sudo dumpcap -b filesize:100000 -b files:100 -i "s2-eth2"  -w $home_dir/defender_output/traces/trace_s2_eth2 -q &

# capturing controller traffcic
# fitler openflow doesn't work
sudo dumpcap -b filesize:100000 -b files:100 -i "docker0"  -f "tcp port 6653" -w $home_dir/defender_output/traces/trace_docker0 -q  




