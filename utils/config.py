import toml

'''
Objects to process TOML config file for BBS system
''' 

class Config():
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config = None

    def parse_config(self) -> None:
        with open(self.config_file, 'r') as f:
            config_text = f.read()
            self.config = toml.loads(config_text)

        if not self.config:
            return False
        
        return True

bbs_config = Config("config.toml")
if not bbs_config.parse_config():
    print("ERROR: Unable to parse config")
    exit(1)

# Global object that holds all the config data when the program is launched
config = bbs_config.config
