"""
This is the script for the fake client scheme in masking MTD
The client here spoods it's IP address adn sends requests to the network 
"""
import time, logging, sys
import urllib.request
import random, math
import ipaddress
import urllib.request  as urllib2
import subprocess


from helpers import get_ip_from_dig_withdig, save_switches, get_ip_from_savefile

def poisson_wait_seconds(lam):
    """ 
    Return next wait time (in seconds) for poisson distribution with lambda requests per 
    second.
    """
    p = random.random()
    inter_arr_time_btw_reqs = (-math.log(1.0 - p) /
                                lam)
    return inter_arr_time_btw_reqs

def get_spoof_ip(prev_ip="10.1.0.10"):
    """NI: randomly generate an ip address and return it """
    spoofed_ip = str(ipaddress.IPv4Address(random.randint(167837696,167903231)))
    # test with constant first
    # spoofed_ip = "10.3.0.10"
    # subprocess.run(["sudo ifconfig fakeclient-eth0 {}".format(spoofed_ip)], shell=True)
    # subprocess.run(["sudo ping -c3 {}".format(get_ip_from_dig_withdig(space=""))], shell=True)
    spoofed_ip = "10.3.0.10"
    return spoofed_ip

def client_loop(wait_time = 60, ip_use_limit=1):
    """Main loop of the client.
    Contacts server with HTTP GET request once every [wait_time] seconds with a 
    fake IP address that is changed every [ip_use_limit] times

    Arguments:
        wait_time: seconds to wait between requests , could include randomness 
        ip_use_limit: how many times one spoofed IP address is used before 
            changing to a new IP
        """

    logger = logging.getLogger('masking client')
    com_type = "HTTP GET"
    
    ### main loop
    lambda_reqspersec = 1/wait_time
    html_files = ["p100kb.html"]#, "p100kb.html", "p100kb.html", "p500kb.html", "p500kb.html", "p500kb.html", "p500kb.html", "p1mb.html", "p1mb.html", "p1mb.html", "p2mb.html", "p3mb.html", "p4mb.html" ]
    logger.info("Sending {} with {} seconds between requests\n".format(com_type, 1/lambda_reqspersec))

    time.sleep(1/lambda_reqspersec)
    ip_use = 0
    client_spoofed_ip = get_spoof_ip()
    while True:
        save_switches("pre trigger")
        server_ip =  get_ip_from_dig_withdig(space="")



        logging.info("Got IP {} sending from spoofed ip {}".format(server_ip, client_spoofed_ip))
        try:
            # proxy = urllib.request.ProxyHandler({"http": "10.1.0.10:49916",
            #                                     "https": "10.1.0.10:49916"}) # does port need to be included?
            # opener = urllib.request.build_opener(proxy)
            # urllib.request.install_opener(opener)
            server_contents = urllib.request.urlopen("http://"+server_ip+"/"+random.choice(html_files), timeout=10).read()
            logging.info("Client recived reply [{}...]".format(server_contents[:12]))
        except urllib.error.HTTPError as e:
            logging.info("Client request returned error {}".format(e))
        except urllib.error.URLError as e:
            logging.info("Client request returned URLerror, may have moved: {}".format(e))
        except Exception as e:
            logging.info("Another exception occured {}".format(e))
        
        save_switches("post trigger")
        
        wait_time = poisson_wait_seconds(lambda_reqspersec)
        logging.info("waiting {} seconds".format(wait_time))
        ip_use += 1
        if ip_use >= ip_use_limit:
            ip_use = 0
            client_spoofed_ip = get_spoof_ip(client_spoofed_ip)
        time.sleep(wait_time)
        

        logging.info("Next client request")

if __name__ == '__main__':
    if len(sys.argv) >=2 :
        if sys.argv[1] == 'h':
            print("python client_script.py [home_dir] [wait_time]")
            sys.exit(0)
        defender_output_dir = sys.argv[1]
    else:
        print("No input, enter: the home dir")
        home_dir = "./data/{}/{}/".format(time.strftime("%y%m%d") , time.strftime("%y%m%d_%H%M"))
        defender_output_dir=home_dir+"defender_output/"
        
    output_file = defender_output_dir+"/fake_clientlog_{}.txt".format(time.strftime("%y%m%d_%H%M%S"))

    logging.basicConfig(
        filename=output_file,
        filemode='w',
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s ::: %(message)s',
        datefmt='%Y%m%d_%H:%M:%S')

    print(sys.argv[2])
    client_loop(wait_time=int(sys.argv[2]))
