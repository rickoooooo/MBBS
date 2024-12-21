from utils.log import logger
from interfaces.comm_interface import CommInterface
from pubsub import pub
import meshtastic.tcp_interface
import time

'''
This interface allows the BBS to communicate over a Meshtastic radio device by using TCP to connect to the device.
'''

class CommInterfaceMeshtasticTCP(CommInterface):
    def __init__(self, radio_ip: str, channel_index: int) -> None:
        self.radio_ip = radio_ip
        self.channel_index = channel_index
        self.interface = meshtastic.tcp_interface.TCPInterface(self.radio_ip)

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