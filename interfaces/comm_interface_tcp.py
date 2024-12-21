from utils.log import logger
from utils.config import config
from utils.log import logger as logger
from interfaces.comm_interface import CommInterface
import threading
import socket
import time

'''
This interface allows a user to connect to the BBS via a TCP socket. This is useful for testing new features or debugging without
needing many radios. It is also faster than waiting for radio packets.
'''

FORMAT = 'UTF-8'

class CommInterfaceTCP(CommInterface):
    def __init__(self, conn, addr: tuple) -> None:
        self.user_id = f"{addr[0]}_{addr[1]}"
        self.conn = conn
        self.addr = addr
        self.hostname = addr[0]
        self.port = addr[1]

    '''
    Send text message over TCP port
    '''
    def send_text(self, text: str, user_id: str) -> None:
        self.conn.send(text.encode())

    '''
    Listen for incoming data on the TCP server
    '''
    def handle_tcp_client(self) -> None:
        logger.info(f"[NEW CONNECTION] {self.hostname}_{self.port} connected.")
        while True:
            data = self.conn.recv(1024)

            if not data:
                break

            packet = self.make_mesh_packet(data)
            self.on_receive(packet, None)

        self.conn.close()

    '''
    Converts the incoming data into something compatible with a Meshtastic packet object.
    '''
    def make_mesh_packet(self, data: bytes) -> dict:
        packet = {}
        packet["from"] = f"{self.hostname}_{self.port}"
        packet["to"] = f"{self.hostname}_{self.port}"
        packet["channel"] = self.port
        packet["decoded"] = {}
        packet["decoded"]["portnum"] = "COMM_INTERFACE_MESHTASTIC_TCP"
        packet["decoded"]["payload"] = data[:-1]
        packet["decoded"]["text"] = data.decode(FORMAT)[:-1]
        packet["id"] = 0
        packet["rxTime"] = int(time.time())
        packet["rxSnr"] = 0
        packet["hopLimit"] = 1
        packet["wantAck"] = "False"
        packet["hopStart"] = 0
        packet["raw"] = ""
        packet["fromId"] = ""
        packet["toId"] = ""

        return packet

    '''
    Close the TCP connection
    '''
    def close(self) -> None:
        self.conn.close()

'''
Starts a TCP server listener. Will create a new thread for each incoming connection.
'''
def tcp_server_start(addr: set) -> None:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(addr)

    server.listen()
    logger.info(f"[LISTENING] TCP server is listening on {config['config']['tcp_server_ip']}:{config['config']['tcp_server_port']}")
    
    while True:
        conn, addr = server.accept()
        tcp_interface = CommInterfaceTCP(conn, addr)
        thread = threading.Thread(target=tcp_interface.handle_tcp_client)
        thread.start()
        logger.info(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

# Get TCP server settings from config.toml.
try:
    addr = (config["config"]["tcp_server_ip"], config["config"]["tcp_server_port"])
except:
    addr = ("", "")
    logger.error("Unable to read TCP server settings from config.toml. Continuing without it.")

# We only run the TCP server if the TCP host and port are configured in config.toml.
if addr != ("", ""):
    tcp_thread = threading.Thread(target=tcp_server_start, args=[addr])
    tcp_thread.start()