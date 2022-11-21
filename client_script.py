"""
Client script
Requests server IP (can assume authenticated), requests the homepage, then sleeps
"""
import time, logging
import urllib.request


from helpers import get_ip_from_dig

def client_loop(wait_time = 60):
    """Main loop of the client.
    Contacts DVWA server with HTTP GET request once every [wait_time] seconds

    Arguments:
        wait_time: seconds to wait between requests , could include randomness 
        """

    logger = logging.getLogger('client')
    com_type = "HTTP GET"
    logger.info("Sending {} with {} seconds between requests\n".format({com_type, wait_time}))
    
    ### main loop
    while True:
        server_ip =  get_ip_from_dig(space="")
        logging.info("Got IP {}".format(server_ip))
        try:
            server_contents = urllib.request.urlopen("http://"+server_ip+"/DVWA").read()
            logging.info("Client recived reply [{}...]".format(server_contents[:12]))
        except urllib.error.HTTPError as e:
            logging.info("Client request returned error {}".format(e))
        time.sleep(wait_time)
        logging.info("Next client request")
        

if __name__ == '__main__':
    home_dir = "./data/{}/{}/".format(time.strftime("%y%m%d") , time.strftime("%y%m%d_%H%M"))
    defender_output_dir=home_dir+"defender_output/"

    output_file = defender_output_dir+"/clientlog_{}.txt".format(time.strftime("%y%m%d_%H%M%S"))

    logging.basicConfig(
        filename=output_file,
        filemode='w',
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s ::: %(message)s',
        datefmt='%Y%m%d_%H:%M:%S')

    client_loop()
