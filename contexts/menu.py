from contexts.context import Context
from utils.message import Message
from utils.config import config
import importlib

'''
This Menu context builds a menu based on a [[menus]] entry in config.toml. It handles user input when selecting a menu option and then
changes the user's session context to the selected option.
'''

class Menu(Context):
    def __init__(self, session: "UserSession", menu_config: dict):
        self.session = session
        self.menu_config = menu_config
        self.name = menu_config["name"]
        self.description = menu_config["description"]
        self.command = menu_config["command"]
        self.message = Message()
        self.message.header = self.name
        self._menu_option_list = list()     # Holds all the options for this menu
        
    '''
    start() is invoked when the session context switches to this menu
    '''
    def start(self) -> None:
        self._menu_option_list = list()

        self.name = self.menu_config["name"]
        self.description = self.menu_config["description"]
        self.command = self.menu_config["command"]
        self.message.header = self.name

        # Loop through all menu options defined in config.toml for this menu
        for option in self.menu_config["options"]:
            # If a special role is defined for this option, ensure the user has access to the role before adding it to their menu.
            if "role" in option:
                if option["role"].lower() != self.session.role.lower():
                    continue

            # If the option is a command, then load that Context object file based on the module and class name specified in the config
            if option["type"] == "command":
                option_module = importlib.import_module(f"contexts.{option['module']}")
                option_class = getattr(option_module, option['class'])
                bbs_option = option_class(self.session, option["command"], option["description"])
                self._menu_option_list.append(bbs_option)

            # If the option is a menu, then always load the Menu context object but initialize it according to the options in config.toml
            elif option["type"] == "menu":
                for menu in config["menus"]:
                    if menu["name"] == option["name"]:
                        new_menu = Menu(self.session, menu)
                        self._menu_option_list.append(new_menu)

        self.message.body = self.get_menu_text()
        self.session.send_message(self.message)

    '''
    get_menu_text() will return this object's menu as a text object. Generally, so you can send it to the user in a message.
    '''
    def get_menu_text(self) -> str:
        menu_text = ""
        for option in self._menu_option_list:
            menu_text += option.description
            if option != self._menu_option_list[-1]:
                menu_text += "\n"
            
        return menu_text

    '''
    Invoked every time a packet comes in for this context.
    '''
    def receive_handler(self, packet: dict) -> None:
        command = self.get_text_input(packet)
        if not command:
            return

        # Loop through all options in the menu list and see if the user chose one of them.
        option = next((item for item in self._menu_option_list if item.command.lower() == command.lower()), None)
        if option:
            self.session.change_context(option)
        else:
            self.send_error("Invalid option!")
