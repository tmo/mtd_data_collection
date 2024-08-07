#!/usr/bin/env python

"""
v6.5:
This is to make it comparable to the diversity data collection, so added fake client who does nothing
topology

                      controller
                      .      .
                     .        .
                    .          .
       client --- ssw1 ------ ssw2 --- server
    fake client --- |
                    |
                    |
                   attacker
"""

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call
import sys, time

def startTBed():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')

    info( '*** Adding controller\n' )
    c0=net.addController(name='c0',
                      controller=RemoteController,
                      ip='172.17.0.2',
                      protocol='tcp',
                      port=6653)

    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch, protocols='OpenFlow13')
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch, protocols='OpenFlow13')

    info( '*** Add hosts\n')
    attacker = net.addHost('attacker', cls=Host, 
            ip='10.2.0.11', 
            mac='00:00:00:00:00:11', defaultRoute=None)
    client = net.addHost('client', cls=Host, 
            ip='10.1.0.10', 
            mac='00:00:00:00:00:22', defaultRoute=None)
    fake_client = net.addHost('fakeclient', cls=Host, 
            ip='10.3.0.10', 
            mac='00:00:00:00:00:44', defaultRoute=None)
    server = net.addHost('server', cls=Host, 
            ip='10.0.0.100', 
            mac='00:00:00:00:00:33', defaultRoute=None)
    # dns = net.addHost('dns', cls=Host, 
    #         ip='10.1.0.20', 
    #         mac='00:00:00:00:00:44', defaultRoute=None)
    info( '*** Add links\n')
    net.addLink(s2, s1)
    net.addLink(s1, client)
    net.addLink(s1, attacker)
    net.addLink(s1, fake_client)
    net.addLink(s2, server)
    # net.addLink(s1, dns)

    info( '*** Starting network\n')
    # alternative to whats in ###
    # net.start() 
    ###
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s1').start([c0])
    net.get('s2').start([c0])

    ###

    return net, [server], [client], [fake_client], [attacker]

def run_experiments(net, server, client, fake_client, attacker, home_dir, client_dir, attacker_dir):
    info( '*** Running host scripts\n')
    net.pingAll()

    # Configuring server 
    # server.cmd("service apache2 stop")
    # server.cmd("service apache2 start")
    server.cmd("source /etc/apache2/envvars")
    server.cmd("apache2 -k graceful-stop")
    time.sleep(3)
    # server.cmd("service nginx restart")
    # server.cmd("service nginx reload")
    server.cmd("ip route add default via 10.0.0.100")
    server.cmd("source /etc/apache2/envvars")
    server.cmd("apache2 -k start -f /etc/apache2/apache2.conf")

    # server.cmd("ip route add default via 10.0.0.100")
    # server.cmd("cd serverfile")
    # server.cmd("python -m http.server")
    

    # start mtd after all hosts have been registered
    server.cmd('sudo docker exec -it onos_new  sh -c "/root/onos/bin/onos-app localhost install! /root/onos/conts/mtd.oar"')
    # server.waitOutput()

    try:
        # run client script
        client.cmd('sudo python client_script.py {} &> {}/direct_logs/client_dirlog.txt &'.format(client_dir, home_dir))

        # fake_client.cmd('sudo python masking_client_script.py {} {} &> {}/direct_logs/fake_client_dirlog.txt &'.format(client_dir, 6, home_dir))
        
        # attacker.cmd('sudo python attacker_script.py {} "dig" "/16" " ," &> {}/direct_logs/attacker_dirlog.txt &'.format(attacker_dir, home_dir))
        CLI(net)
    except KeyboardInterrupt as e:
        net.stop()

if __name__ == '__main__':
    if len(sys.argv) >=3 :
        print("LEN OF ERROR", len(sys.argv))
        home_dir = sys.argv[1]
        client_dir = sys.argv[2]
        attacker_dir = sys.argv[3]
    else: 
        raise(Exception("Must input home dir, client dir, attacker dir"))
    setLogLevel( 'info' )

    # tbed_args  = startTBed()
    # run_experiments(*tbed_args,  home_dir, client_dir, attacker_dir)

    net, [server], [client], [fake_client], [attacker]  = startTBed()
    run_experiments(net, server, client, fake_client, attacker,  home_dir, client_dir, attacker_dir)



