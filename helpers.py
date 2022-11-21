import logging
import os
import re

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