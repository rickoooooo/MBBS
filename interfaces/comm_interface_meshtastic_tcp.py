from utils.log import logger
from interfaces.comm_interface import CommInterface
from pubsub import pub
import meshtastic.tcp_interface
import threading
import time
import socket

'''
This interface allows the BBS to communicate over a Meshtastic radio device by using TCP to connect to the device.
'''

class CommInterfaceMeshtasticTCP(CommInterface):
    def __init__(self, radio_ip: str, bc_channel_index: int) -> None:
        self.radio_ip = radio_ip
        self.bc_channel_index = bc_channel_index
        self.interface = meshtastic.tcp_interface.TCPInterface(self.radio_ip, connectNow=True)

        self.monitor_thread = threading.Thread(target=self.check_socket_closed)
        self.monitor_thread.start()

        # Meshtastic uses pubsub to receive messages from the radios asynchronously
        pub.subscribe(self.on_receive, "meshtastic.receive")
        pub.subscribe(self.on_connection, "meshtastic.connection.established")
        pub.subscribe(self.on_disconnect, "meshtastic.connection.lost")

    '''
    Called when we (re)connect to the radio
    '''
    def on_connection(self, interface: CommInterface, topic=pub.AUTO_TOPIC) -> None: 
        # defaults to broadcast, specify a destination ID if you wish
        logger.info("Connected to radio.")
        self.send_broadcast("BBS Online!")

    '''
    Called when we lose connection to the radio
    '''
    def on_disconnect(self, interface: CommInterface) -> None:
        self.interface_reset()

    '''
    Send text message over TCP port to the Meshtastic radip
    '''
    def send_text(self, text: str, user_id: str) -> None:
        self.interface.sendText(
            text,
            user_id,
            wantAck=True
        )

    '''
    Send broadcast message on configured channel index
    '''
    def send_broadcast(self, text:str) -> None:
        self.interface.sendText(
            text,
            channelIndex=self.bc_channel_index,
            wantAck=True
        )

    '''
    Close the meshtastic TCP connection
    '''
    def close(self) -> None:
        self.interface.close()

    '''
    Hack to test if the TCP socket is still open
    Meshtastic radio only allows one connection at a time. If anything else touches the port, it will disconnect the BBS.
    The Meshtastic API connection.lost topic doesn't seem to get triggered right away and we won't see incomming packets until the connection is reset
    '''
    def check_socket_closed(self) -> bool:
        while True:
            sock = self.interface.socket
            try:
                # this will try to read bytes without blocking and also without removing them from buffer (peek only)
                data = sock.recv(16, socket.MSG_DONTWAIT | socket.MSG_PEEK)
                if len(data) == 0:
                    self.interface_reset()
            except BlockingIOError:
                pass  # socket is open and reading from it would block
            except ConnectionResetError:
                self.interface_reset()  # socket was closed for some other reason
            except Exception as e:
                logger.error(str(e))
                pass
            time.sleep(1)

    '''
    Resets the TCP interface if it was disconnected for some reason
    '''
    def interface_reset(self) -> None:
        self.interface.close()
        self.interface = meshtastic.tcp_interface.TCPInterface(self.radio_ip, connectNow=True)

