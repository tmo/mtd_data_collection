#!/bin/bash
# Runs complete simulation to take data

today=$(date +"%y%m%d")
hour=$(date +"%H%M")
data_time="${today}_${hour}"
home_dir="./data/${today}/${today}_${hour}"

export home_dir

# make folder structure
sudo mkdir -p $home_dir/defender_output/snort_output $home_dir/attacker_output/traces $home_dir/direct_logs

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
sudo docker cp ./mtd_apps/real_drop_cidr16_m300_onos-app-mtd-2.4.0.oar  onos_new:/root/onos/conts/mtd.oar
sleep 20
# sudo docker exec -it onos_new  sh -c "/root/onos/bin/onos-app localhost install! /root/onos/conts/mtd_drop_60.oar"
echo "Finished running onos"

# run mtd inotify, this notifies whenever the IP address of a host changes
sudo killall inotifywait
# sudo sh ./mod_mtd_notify.sh &> $home_dir/defender_output/mtd_times_$data_time.txt &
sudo bash -c "./mod_mtd_notify.sh &>> $home_dir/defender_output/mtd_times_$data_time.txt" &


# run testbed and scripts for each host
# sudo mn -c && sudo -E python ./testbed/testbed_topo_TCP_v5.py $home_dir $home_dir/defender_output/ $home_dir/attacker_output/ 
sudo killall xterm
sudo -E xterm -hold -e bash -c "sudo mn -c && sudo -E python ./testbed/testbed_topo_TCP_v6.py $home_dir $home_dir/defender_output/ $home_dir/attacker_output/ " &

# wait for interfaces to be up
sleep 30
# start snort
# this only tracks the server IPs
sudo bash -c "sudo snort -c /etc/snort/snort.conf -i s1-eth1 -h 10.0.0.100/16 -l $home_dir/defender_output/snort_output -A fast &> $home_dir/direct_logs/snort_dirlog.txt &" &

# might be best to later intentionally name links, but for now can type net to track connections
# run packet capture, on all links from simulated switch 1
sudo dumpcap -b filesize:100000 -b files:100 -i "s1-eth1" -i "s1-eth2" -i "s1-eth3"  -w $home_dir/attacker_output/traces/trace -q &

