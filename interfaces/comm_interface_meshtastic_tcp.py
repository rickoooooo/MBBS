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
    def __init__(self, radio_ip: str, channel_index: int) -> None:
        self.radio_ip = radio_ip
        self.channel_index = channel_index
        self.interface = meshtastic.tcp_interface.TCPInterface(self.radio_ip)

        self.monitor_thread = threading.Thread(target=self.check_socket_closed)
        self.monitor_thread.start()

        # Meshtastic uses pubsub to receive messages from the radios asynchronously
        pub.subscribe(self.on_receive, "meshtastic.receive")
        pub.subscribe(self.on_connection, "meshtastic.connection.established")

    '''
    Called when we (re)connect to the radio
    '''
    def on_connection(self, interface: CommInterface, topic=pub.AUTO_TOPIC) -> None: 
        # defaults to broadcast, specify a destination ID if you wish
        logger.info("Connected to radio.")
        #interface.sendText("BBS Online!")

    '''
    Send text message over TCP port to the Meshtastic radip
    '''
    def send_text(self, text: str, user_id: str) -> None:
        self.interface.sendText(
            text,
            user_id,
            wantAck=True,
            channelIndex=self.channel_index
            #onResponse=self.menu.option_handler(packet, self.interface)
        )

    '''
    Close the meshtastic TCP connection
    '''
    def close(self) -> None:
        self.interface.close()

    '''
    Hack to test if the TCP socket is still open
    Meshtastic radio only allows one connection at a time. If anything else touches the port, it will disconnect the BBS.
    The Meshtastic API doesn't currently have a way to monitor and handle this condition, so we test here and reset as needed.
    '''
    def check_socket_closed(self) -> bool:
        while True:
            sock = self.interface.socket
            try:
                # this will try to read bytes without blocking and also without removing them from buffer (peek only)
                data = sock.recv(16, socket.MSG_DONTWAIT | socket.MSG_PEEK)
                if len(data) == 0:
                    self.socket_reset()
            except BlockingIOError:
                pass  # socket is open and reading from it would block
            except ConnectionResetError:
                self.socket_reset()  # socket was closed for some other reason
            except Exception as e:
                logger.error(str(e))
                pass
            time.sleep(1)

    '''
    Resets the TCP interface if it was disconnected for some reason
    '''
    def socket_reset(self) -> None:
        self.interface.close()
        self.interface = meshtastic.tcp_interface.TCPInterface(self.radio_ip)

