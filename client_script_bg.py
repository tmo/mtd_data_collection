"""
Client script
Requests server IP (can assume authenticated), requests the homepage, then sleeps
"""
import time, logging, sys
import urllib.request
import random


from helpers import get_ip_from_dig_withdig, save_switches

def client_loop(wait_time = 60):
    """Main loop of the client.
    Contacts DVWA server with HTTP GET request once every [wait_time] seconds

    Arguments:
        wait_time: seconds to wait between requests , could include randomness 
        """

    logger = logging.getLogger('client')
    com_type = "HTTP GET"
    logger.info("Sending {} with {} seconds between requests\n".format(com_type, wait_time))
    
    html_files = ["index.html",  "p1mb.html",  "p2mb.html",  "p3mb.html",  "p4mb.html",  "p500kb.html"  "page.html"]
    time.sleep(5)
    while True:
        logging.info("Requesting eserver")
        try:
            server_contents = urllib.request.urlopen("http://10.3.0.100/"+random.choice(html_files), timeout=300).read()
            logging.info("Client recived reply [{}...]".format(server_contents[:12]))
        except urllib.error.HTTPError as e:
            logging.info("Client request returned error {}".format(e))
        except urllib.error.URLError as e:
            logging.info("Client request returned URLerror, may have moved: {}".format(e))
        except Exception as e:
            logging.info("Another exception occured {}".format(e))

        # if (time.time() - start_time) > total_sec:
        #     start_time = time.time()
        #     # loop_length +=1
        time.sleep(random.randint(10,15))
        logging.info("Next client request")

def client_persistant_loop(wait_time = 60):
    """Main loop of the client.
    Monitors for when mtd triggers then
    Contacts DVWA server with HTTP GET request once every [wait_time] seconds
    (this is to somewhat simulate an ongoing connection that gets interrupted)

    Arguments:
        wait_time: seconds to wait between requests , could include randomness 
        """
    pass
    logger = logging.getLogger('client')
    com_type = "HTTP GET"
    logger.info("Sending {} with {} seconds between requests\n".format(com_type, wait_time))
    
    ### main loop
    while True:
        server_ip =  get_ip_from_dig_withdig(space="")
        logging.info("Got IP {}".format(server_ip))
        try:
            server_contents = urllib.request.urlopen("http://"+server_ip+"/DVWA").read()
            logging.info("Client recived reply [{}...]".format(server_contents[:12]))
        except urllib.error.HTTPError as e:
            logging.info("Client request returned error {}".format(e))
        except urllib.error.URLError as e:
            logging.info("Client request returned URLerror, may have moved: {}".format(e))
        except Exception as e:
            logging.info("Another exception occured {}".format(e))

        time.sleep(wait_time)
        logging.info("Next client request") 

if __name__ == '__main__':
    if len(sys.argv) >=2 :
        if sys.argv[1] == 'h':
            print("python client_script_bg.py [home_dir]")
            sys.exit(0)
        defender_output_dir = sys.argv[1]
    else:
        print("No input, enter: the home dir")
        home_dir = "./data/{}/{}/".format(time.strftime("%y%m%d") , time.strftime("%y%m%d_%H%M"))
        defender_output_dir=home_dir+"defender_output/"
        
    output_file = defender_output_dir+"/clientbglog_{}.txt".format(time.strftime("%y%m%d_%H%M%S"))

    logging.basicConfig(
        filename=output_file,
        filemode='w',
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s ::: %(message)s',
        datefmt='%Y%m%d_%H:%M:%S')


    client_loop(wait_time=13)#sys.argv[2]
