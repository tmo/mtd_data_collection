import logging
import os
import re
import subprocess

def get_ip_from_dig(space="/16"):
    """Finds vIP address of host and return the space to search for it.
    Used for creating smaller search spaces for testing.
    
    Arguments:
        space: the search space to append, with format "/n" 
    """
    with open(os.path.abspath("/etc/bind/zones/forward.mj.uq.dslab.com.db"), 'r') as f:      
        ip = f.read()

    ip_addr = re.findall("[1-9].*", re.findall(r'www\sIN\sA\s.*',ip)[0])[0]
    # subprocess.check_output("dig www.mj.uq.dslab.com  @192.168.31.128   +short", shell=True)
    # ip = ip[::-1].split(".",1)[1][::-1]+".*"
    # space = "/16"
    ip_space = ip_addr + space
    logging.info("Got ip space {} from dig ".format(ip_space))
    return ip_space

def get_ip_from_dig_withdig(space="/16"):
    """Finds vIP address of host and return the space to search for it.
    Used for creating smaller search spaces for testing.
    Also sends a dig request but the result is not used
    
    Arguments:
        space: the search space to append, with format "/n" 
    """
    # just run this to get a dns request (see notes 16/01)
    #if wait 5 seconds so just 65, otherwise ends after tcp connection done
    # try: # should not wait for it to finish now
    #     subprocess.Popen(["dig www.mj.uq.dslab.com @10.1.0.20 +short +retry=0"], shell=True)
    # except Exception as e:
    #     print(e)

    with open(os.path.abspath("/etc/bind/zones/forward.mj.uq.dslab.com.db"), 'r') as f:      
        ip = f.read()

    ip_addr = re.findall("[1-9].*", re.findall(r'www\sIN\sA\s.*',ip)[0])[0]


    
    # ip = ip[::-1].split(".",1)[1][::-1]+".*"
    # space = "/16"
    ip_space = ip_addr + space
    logging.info("Got ip space {} from dig ".format(ip_space))
    return ip_space


def save_switches(info_to_print):
    print(info_to_print)
    try: # should not wait for it to finish now
        subprocess.run(["echo $(date +'%T.%5N') sw1"], shell=True)
        subprocess.run(["sudo ovs-ofctl dump-flows s1  --protocols=OpenFlow13 "], shell=True)
        subprocess.run(["echo $(date +'%T.%5N') sw2"], shell=True)
        subprocess.run(["sudo ovs-ofctl dump-flows s2  --protocols=OpenFlow13"], shell=True)
    except Exception as e:
        print(e)
    print(info_to_print)