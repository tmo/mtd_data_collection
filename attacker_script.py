"""
Data taking script
Performs nmap scans and records the outcome
"""
from asyncio import subprocess
import time, sys, logging
import subprocess
import os
import re

from helpers import get_ip_from_dig

def attacker_loop(settings,
                    base_ip = "dig",
                    ip_space = "/16",
                    test_flags = [
                        # "-sn",
                        # "-PS",
                        # "-PA",
                        # "-PU",
                        # "-PE",
                        # "-PS -sn",
                        # "-PA -sn",
                        # "-sS",
                        # "-sT",
                    ],
                    test_ports = [
                        # "-PS -p80,443",
                        # "-PA -p80,443",
                        # "-PU -p80,443",
                        # "-PE -p80,443",
                        "-sS -p80,443",
                        # "-sT -p80,443",
                    ]
                    ):
    """Main loop of the attacker, runs nmap with every combination of test_flags
    and test_ports.

    Arguments:
        settings: config settings to be saved to file, usually topology 
                    and mtd settings
        base_ip: base ip to apply ip range to. will find host IP from dig by 
                    default or  "dig"
        ip_space: ip range to scan, /16 by default
        test_flags: list of strings of flags to pass to nmap
        test_ports: list of string of ports to pass to nmap
        """

    logger = logging.getLogger('attacker')
    logger.info("Settings: {} \n".format({settings}))
    
    ### main loop
    while True:
        for scan_flags in test_flags + test_ports:
            if base_ip != "dig":
                ip_range = base_ip + ip_space
            else:
                ip_range = get_ip_from_dig(space=ip_space)
            logger.info("Iprange {}".format(ip_range))

            cmd_str = "sudo nmap "+ scan_flags  + " -oG - " + ip_range
            logger.info("running {}".format(cmd_str))
            
            try:
                scan_out = subprocess.check_output(cmd_str,shell=True).decode("utf-8")
                nmap_short_success = True if scan_out.find("Up")>0 else False
                logger.info("Output:  {} ".format(scan_out))
                logger.info("Success: {} ".format(nmap_short_success))
            except KeyboardInterrupt as e:
                logger.info("interrupted")
                sys.exit(-1)
            except:
                logger.info("nmap failed with error {} ".format(scan_out))
            logger.info("Next Scan")

if __name__ == '__main__':
    if len(sys.argv) >=2 :
        attacker_output_dir = sys.argv[1]
        base_ip = sys.argv[2]
        ip_space = sys.argv[3]
        settings = sys.argv[4]
    else:
        print("No input, enter: attacker's directory, base ip, ip_space,  and settings to be saved")
        home_dir = "./data/{}/{}/".format(time.strftime("%y%m%d") , time.strftime("%y%m%d_%H%M"))
        attacker_output_dir=home_dir+"attacker_output/"
        base_ip="10.0.0.100"
        ip_space="/16"
        settings="unknown"
 
    output_file = attacker_output_dir+"/attackerlog_{}.txt".format(time.strftime("%y%m%d_%H%M%S"))

    logging.basicConfig(
        filename=output_file,
        filemode='w',
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s ::: %(message)s',
        datefmt='%Y%m%d_%H:%M:%S')

    # other inputs: base ip or from dig, base /16 ect
    attacker_loop(settings, base_ip, ip_space)
