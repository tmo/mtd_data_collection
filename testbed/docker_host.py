from mininet.net import Mininet
from mininet.node import Controller, RemoteController, Host, Node
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import Link, Intf, TCLink
from mininet.topo import Topo
from mininet.util import dumpNodeConnections
from mininet.util import isShellBuiltin
from subprocess import call, check_output
from subprocess import Popen, PIPE, STDOUT
import logging
import os 
import time
import select
import re

# modified from  https://github.com/Talentica/of_odl/blob/master/topology/fattree.py
class DockerHost( Host ):
    "Docker host"
    def __init__( self, name, image='myhttpd:latest', dargs=None, startString=None, **kwargs ):
        self.image = image
        self.dargs = dargs
        if startString is None:
            self.startString = None#"-c /bin/bash"
            self.dargs = "-d"
        else:
            self.startString = startString
        Host.__init__( self, name, **kwargs )

    #def cmd( self, *args, **kwargs ):
    #    print "cmd sending "+str(args)
    #    ret=Host.cmd(self, *args, **kwargs )
    #    print ret
    #    return ret

    def sendCmd( self, *args, **kwargs ):
        """Send a command, followed by a command to echo a sentinel,
           and return without waiting for the command to complete.
           args: command and arguments, or string
           printPid: print command's PID?"""
        print('got commmand = ')
        print(args)
        assert not self.waiting
        printPid = kwargs.get( 'printPid', True )
        # Allow sendCmd( [ list ] )
        if len( args ) == 1 and type( args[ 0 ] ) is list:
            cmd = args[ 0 ]
        # Allow sendCmd( cmd, arg1, arg2... )
        elif len( args ) > 0:
            cmd = args
        cmdorig = cmd
        # Convert to string
        if not isinstance( cmd, str ):
            cmd = ' '.join( [ str( c ) for c in cmd ] )
        if not re.search( r'\w', cmd ):
            # Replace empty commands with something harmless
            cmd = 'echo -n'
        self.lastCmd = cmd
        printPid = printPid and not isShellBuiltin( cmd )
        #new_cmd = ['docker', 'exec', "mininet-"+self.name]
        #new_cmd = new_cmd + list(cmdorig)
        new_cmd = 'docker exec ' + "mininet-"+self.name + ' ' + cmd
        call(new_cmd, shell=True)
        '''pidp = Popen( new_cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=False )
        ps_out = pidp.stdout.readlines()
        if not ps_out:
            print 'no output'
        else:
            print ps_out[0]
        call("sleep 2", shell=True) '''
        '''if len( cmd ) > 0 and cmd[ -1 ] == '&':
            # print ^A{pid}\n{sentinel}
            cmd += ' printf "\\001%d\n\\177" $! \n'
        else:
            # print sentinel
            cmd += '; printf "\\177"'
        self.write( cmd + '\n' ) 
        call("sleep 2", shell=True)
        self.lastPid = None
        self.waiting = False'''

    def popen( self, *args, **kwargs ):
        """Return a Popen() object in node's namespace
           args: Popen() args, single list, or string
           kwargs: Popen() keyword args"""
        # Tell mnexec to execute command in our cgroup
        mncmd = [ 'docker', 'attach', "mininet-"+self.name ]
        return Host.popen( self, *args, mncmd=mncmd, **kwargs )

    def terminate( self ):
        "Send kill signal to Node and clean up after it."
        if self.shell:
            call(["docker stop mininet-"+self.name], shell=True)
        self.cleanup()

    def startShell( self ):
        "Start a shell process for running commands"
        if self.shell:
            error( "%s: shell is already running" )
            return
        # Remove any old container with this name
        print("Removing any old host still running")
        call(["docker stop mininet-"+self.name], shell=True)
        call(["docker rm mininet-"+self.name], shell=True)
        # call(["sudo docker run --privileged -h mn-eserver --name=mininet-eserver -d --net='none' httpd:2.4"], shell=True)
        # Create run command
        print("Start Docker Host")
        cmd = ["sudo", "-E", "docker","run","--privileged","-h","mn-"+self.name ,"--name=mininet-"+self.name]
        if self.dargs is not None:
            cmd.extend([self.dargs])
        # cmd.extend(["--net='none'",self.image])
        cmd.extend(["--net='none'",self.image,self.startString])
        print(cmd);
        cmd = [f"sudo docker run --privileged -h mn-{self.name } --name=mininet-{self.name} -d --net='none' {self.image}"]
        self.shell = Popen( cmd,  stdin=PIPE, stdout=PIPE, stderr=STDOUT, shell=True, close_fds=True)
        self.shell.wait()
        self.stdin = self.shell.stdin
        self.stdout = self.shell.stdout
        self.pid = self.shell.pid
        self.pollOut = select.poll()
        self.pollOut.register( self.stdout )
        # Maintain mapping between file descriptors and nodes
        # This is useful for monitoring multiple nodes
        # using select.poll()
        self.outToNode[ self.stdout.fileno() ] = self
        self.inToNode[ self.stdin.fileno() ] = self
        self.execed = False
        self.lastCmd = None
        self.lastPid = None
        self.readbuf = ''
        self.waiting = False

        print(self.pid)
        call("sleep 2", shell=True)
        pid_cmd = ["sudo", "docker","inspect","--format='{{ .State.Pid }}'","mininet-"+self.name]
        pidp = Popen( pid_cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=False )
        print(pidp)
        # print(pidp.communicate())
        ps_out = pidp.stdout.readlines()
        print("pid:", type(ps_out[0]), str(ps_out[0]), re.sub("[^0-9]", "",str(ps_out[0])))
        # print(ps_out)
        self.pid = int(re.sub("[^0-9]", "",str(ps_out[0])))


