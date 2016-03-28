import sys
import redis
TOKEN = "" #token
ADMINS = [120733229]#admins
BOTINFO = ""
HUMMINGBIRD = ["",""] #user, pass
VNDB = ["", ""]#user, pass
SHIKI = ["",""]#user, pass


# BE CAREFUL, SOME PLUGINS COULD DAMAGE YOUR DEVICE
PLUGINS = ["arcbaka", "archelp", "arcshiki", "archummingbird"]

plugins = []
DB = None

def initRedis():
    global  DB
    DB = redis.StrictRedis()


def registerPlugins():
    global plugins
    plugins = []
    sys.path.append("./plugins")
    for pluginName in PLUGINS:
        if not pluginName.startswith("arc"):
            print("Wrong plugin %s " % pluginName, file=sys.stderr)
            continue
        try:
            tmp = __import__(pluginName)
            if test_plugin(tmp):
                plugins.append(tmp)
                print("Registered plugin", pluginName)
        except Exception as e:
            print(e, file=sys.stderr)


def test_plugin(plugin):
    return True

