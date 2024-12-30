from utils.log import logger
from utils.session_db import session_db
from utils.config import config
from utils.user_session import UserSession

'''
This acts as a base class for other communication interfaces. Current build-in comm interfaces are functional for Meshtastic
packets via connecting to a Meshtastic device over TCP, and a simple TCP socket server interface which is helpful for debugging
and testing new features. Other interfaces can be build in this 'interfaces' subdirectory, though code would need to be updated to
instantiate the new interface.
'''

ACTIVATE_KEYWORD = config["main"]["activate_keyword"]
AUTHORIZED_PORTNUMS = [
    "TEXT_MESSAGE_APP",                 # Meshtastic chat app
    "COMM_INTERFACE_MESHTASTIC_TCP"     # Custom PORTNUM created in the CommInterfaceTCP object.
    ]

class CommInterface:
    def __init__(self) -> None:
        pass

    '''
    send_text() will send a text message to a user via this interface. Must be implemented by the child class.
    '''
    def send_text(self, text: str, user_id: str) -> None:
        pass

    '''
    on_receive() is called when a packet arrives on this interface.
    This function must identify what session the packet is destined for, and then invoke that session's receive_message() handler.
    Alternatively, if the packet does not belong to a session, it must be able to create a new session as needed.
    '''
    def on_receive(self, packet: dict, interface) -> None:
        # Only process messages from Meshtastic or from custom interfaces.
        if "decoded" in packet and packet["decoded"]["portnum"] in AUTHORIZED_PORTNUMS:
            logger.debug("Incoming packet")
            if "from" in packet:
                user_id = packet["from"]

                # Does user have a session currently?
                if session_db.check_session(user_id):
                    logger.debug("User has session")

                    # If the interface is None, it's because the connection is not from the Mesh but from TCP or something else
                    if interface != None:
                        # Ensure the incoming packet is addressed to us. If not, just return
                        bbs_node_id = interface.getMyNodeInfo()["num"]
                        if packet["to"] != bbs_node_id:
                            return

                    if "text" in packet["decoded"]:
                        session = session_db.get_session(user_id)
                        if session:
                            session.receive_message(packet)
                        else:
                            logger.error("User had a session but suddenly doesn't...")

                # User doesn't have a session, so create a new one
                else:
                    if "text" in packet["decoded"] and packet["decoded"]["text"].lower() == ACTIVATE_KEYWORD:
                        session = UserSession(user_id, self, packet)
                        session_db.add_session(user_id, session)
                        logger.info(f"User {user_id} connected to BBS!")

