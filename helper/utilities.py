import configparser

def get_config(section: str) -> dict:
    config = configparser.ConfigParser()
    config.read('../app/config.ini')
    info = dict()
    for key in config[section]:
        info[key] = config[section][key]
    return info

