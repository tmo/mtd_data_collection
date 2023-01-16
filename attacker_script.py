"""
Data taking script
Performs nmap scans and records the outcome
"""
from asyncio import subprocess
import time, sys, logging, random 
import subprocess, threading
import os, re
import re

from helpers import get_ip_from_dig


def probing_attacker_action(scan_flags, ip_range, logger):
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



def continuous_probe(ip, avg_t = 10):
    """
    continuously probe one ip address over time
    ip:
    avg_t : 
    """
    connected = True
    while connected == True:
        # scan just one IP
        out = subprocess.check_output(['nmap', '-sn', ip]).decode("utf-8")
        third_line = out.split("\n")[2]
        if (third_line[0] == "H"):
            # host is up
            print("{} TEMP: connected to host".format( time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            wait_time = random.randrange(1, 10)
            sys.stdout.flush()
            time.sleep(wait_time) 
        elif (third_line[0] == "N"):
            # host is down
            print("{} TEMP: lost connection to host".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            connected = False
            sys.stdout.flush()
            return # this should end the thread

        else:
            print("{} TEMP: got somethign else {}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), out))
            return

def coninuous_probing_attacker_action(scan_flags, ip_range, logger):
    """ psudo code:
    Find an ip address in use ( how to get output while scan ongoing) (-v)
    Continue scan
    when found try connection
        if fialed restart
        if not failed, retry and 10 seconds
    try connection,
    if failed, do an nmap scan
    if not failed, retry in 10 seconds   
    """

     # reduced max host groups so print clsoer to time of mtd, each should take 
     # 30 seconds or less
    # ip_range = get_ip_from_dig(space="/24")
    cmd_str = "sudo nmap "+ scan_flags  + " --max-hostgroup 64 -oG - -n --disable-arp-ping " + ip_range
    logger.info("running {}".format(cmd_str))
    
    try:

        # scan_out = subprocess.check_output(cmd_str,shell=True).decode("utf-8")
        # launch process running command, and get output
        scan_proc = subprocess.Popen(cmd_str, shell=True, stdin=subprocess.PIPE, 
                                                        stdout=subprocess.PIPE,
                                                        stderr=subprocess.PIPE)
        with scan_proc.stdout: # otherwise would need to clsoe at the end
            for line in iter(scan_proc.stdout.readline, b''):
                # print out the port line since all will show up, print only success
                # since skipping discovery means all printed as filtered
                sline = str(line)
                # check output to see if IP found every time it writes
                if "Ports" in sline and (("/closed" in sline) or ("/open" in sline)):
                    nmap_short_success = True if (("/closed" in sline) or ("/open" in sline)) else False
                    logger.info("Output:  {} ".format(sline))
                    logger.info("Success: {} ".format(nmap_short_success))
                    # if IP found, launch subroutine
                    # extract IP
                    ip_pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
                    found_ip = ip_pattern.search(sline)[0]
                    th = threading.Thread(target=continuous_probe, args=(found_ip,))
                    th.start()
                    th.join()
                    print("{} TEMP: moving to next line".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
                    sys.stdout.flush()
                    # assume one host so stop scan (TODO)
                    # scan_proc.kill()
                    break
                if not (any(hed in sline for hed in ["Ports:", "Status:", "//"])):
                    # either final line or something else unexpected
                    logger.info("Output:  {} ".format(sline))
                # if not wait for next output
        # do so until process terminates
        scan_proc.kill()
        print(scan_proc.poll())
        scan_proc.wait() # wait for exit
        print(scan_proc.communicate())

        # print output

    except KeyboardInterrupt as e:
        logger.info("interrupted")
        sys.exit(-1)
    except Exception as e:
        logger.info("nmap failed with error {} ".format(e))


def connecting_attacker_action():
    pass


def attacker_loop(settings,
                    attacker_action_fn,
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
                        "-sS -Pn -p80,443",
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

            attacker_action_fn(scan_flags, ip_range, logger)
            logger.info("Next Scan")

if __name__ == '__main__':
    if len(sys.argv) >=2 :
        if sys.argv[1] == 'h':
            print("python attacker_script.py [attacker_directory] [base_ip] [ip_space] [settings to be saved]")
            sys.exit(0)
        attacker_output_dir = sys.argv[1]
        base_ip = sys.argv[2]
        ip_space = sys.argv[3]
        settings = sys.argv[4]
    else:
        print("No input, enter: attacker's directory, base ip, ip_space,  and settings to be saved")
        home_dir = "./data/{}/{}/".format(time.strftime("%y%m%d") , time.strftime("%y%m%d_%H%M"))
        attacker_output_dir=home_dir+"attacker_output/"
        base_ip="dig" #"10.0.0.100"
        ip_space="/24"
        settings="unknown"
 
    output_file = attacker_output_dir+"/attackerlog_{}.txt".format(time.strftime("%y%m%d_%H%M%S"))

    logging.basicConfig(
        filename=output_file,
        filemode='w',
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s ::: %(message)s',
        datefmt='%Y%m%d_%H:%M:%S')

    print("hi")
    sys.stdout.flush()
    # other inputs: base ip or from dig, base /16 ect
    attacker_loop(settings, coninuous_probing_attacker_action, base_ip, ip_space)
