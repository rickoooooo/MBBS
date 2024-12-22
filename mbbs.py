import meshtastic
import meshtastic.tcp_interface
import time
from pubsub import pub
from utils.log import logger as logger
from utils.config import config
from interfaces.comm_interface_tcp import CommInterfaceTCP
from interfaces.comm_interface_meshtastic_tcp import CommInterfaceMeshtasticTCP
from interfaces.comm_interface_meshtastic_serial import CommInterfaceMeshtasticSerial

'''
This is the main application. Edit the config file at config.toml to configure the program, then launch this.
'''

if __name__ == '__main__':    
    interface = None
    serial_interface = None

    # Meshtastic radio TCP interface
    try:
        radio_ip = config["interface_mesh_tcp"]["radio_ip"]
        radio_channel = config["main"]["radio_channel"]
    except: 
        logger.error("Unable to read radio's TCP config options from config.toml. Continuing without it.")
    else:
        interface = CommInterfaceMeshtasticTCP(radio_ip, radio_channel)

    # Meshtastic radio serial interface
    try:
        radio_device = config["interface_mesh_serial"]["serial_device"]
        radio_channel = config["main"]["radio_channel"]
    except:
        logger.error("Unable to read serial device path from config.toml. Continuing without it.")
    else:
        serial_interface = CommInterfaceMeshtasticSerial(radio_device, radio_channel)   

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Shutting down the server...")

        if interface:
            interface.close()

        if serial_interface:
            serial_interface.close()

        try:
            if js8call_client.connected:
                js8call_client.close()
        except:
            pass

