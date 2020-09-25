import system_utils
import conf

def hello():
    return system_utils.hello()

def config():
    return conf.readConfig()
