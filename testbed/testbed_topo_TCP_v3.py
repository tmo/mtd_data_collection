#!/usr/bin/env python

"""
v3:
Modifying v1 (Autogenerated from miniedit) based on working 
topology

                  controller
                  .      .
                 .        .
                .          .
   client --- ssw1 ------ ssw2 --- server
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
    server = net.addHost('server', cls=Host, 
            ip='10.0.0.100', 
            mac='00:00:00:00:00:33', defaultRoute=None)

    info( '*** Add links\n')
    net.addLink(s2, s1) #cls=TCLink, bw=1000, delay='1ms', loss=1)
    net.addLink(s1, client)
    net.addLink(s1, attacker)
    net.addLink(s2, server)

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

    info( '*** Post configure switches and hosts\n')
    ###
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    startTBed()

