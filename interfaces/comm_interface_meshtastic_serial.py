from utils.log import logger
from interfaces.comm_interface import CommInterface
from pubsub import pub
import meshtastic.serial_interface
import time

'''
This interface allows the BBS to communicate over a Meshtastic radio device by using a serial port (USB connection) to connect to the device.
'''

class CommInterfaceMeshtasticSerial(CommInterface):
    def __init__(self, device: str, channel_index: int) -> None:
        self.channel_index = channel_index
        self.device = device
        self.interface = meshtastic.serial_interface.SerialInterface(devPath=self.device)

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
