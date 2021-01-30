import json
import os
import os.path as path
import sys
import subprocess

from pathlib import Path

HOME = str(Path.home())

ConfigFilePath = path.join(HOME, ".config", "update-not-ppa-deb.json")

CacheFolder = path.join(HOME, ".cache", "not-ppa-deb")

args = sys.argv

if not path.isdir(path.join(HOME, ".config")):
    os.mkdir(path.join(HOME, ".config"))

if not path.isdir(path.join(HOME, ".cache")):
    os.mkdir(path.join(HOME, ".cache"))

if not path.isfile(ConfigFilePath):
    print("Initializing not-ppa-deb config.")
    file = open(ConfigFilePath, 'w')
    file.write(json.dumps({"debs": []}))
    file.close()
    print("Initialized")

if not path.isdir(CacheFolder):
    os.mkdir(CacheFolder)

print("Reading config")
configFile = open(ConfigFilePath, 'r')
config = json.loads(configFile.read())
configFile.close()
print("Config read")



def installDeb(id, url):
        print("Downloading " + id + ".deb")
        subprocess.run(["curl", url, "-s", "-L", "-J",
                        "-o", id + ".deb", "--next"
                        ], cwd=CacheFolder)
        print("Done")
        print("Installing " + id + ".deb")
        subprocess.run(["sudo", "dpkg", "-i", id + ".deb"], cwd=CacheFolder)
        print("Done")
        print("Cleaning cache")
        subprocess.run(["rm", id + ".deb"], cwd=CacheFolder)
        print("Done")





def readConfig():
    global configFile
    global config
    configFile = open(ConfigFilePath, 'r')
    config = json.loads(configFile.read())
    configFile.close()


def writeConfig():
    global config
    global configFile
    configFile = open(ConfigFilePath, 'w')
    configFile.write(json.dumps(config))
    configFile.close()
    readConfig()


def help():
    print("HELP")


def list():
    global config
    print("Installed packages:")
    for i in config["debs"]:
        print("-" + i["id"] + ":", i["url"])


def install():
    if len(args) > 3:
        deb_id = args[2]
        deb_url = args[3]
        config["debs"].append({"id": deb_id, "url": deb_url})
        installDeb(deb_id, deb_url)
        writeConfig()
    else:
        print("Not enough arguments!")


def remove():
    print("remove")


def update():
    print("Upgrading not-ppa-debs:")
    global config
    for i in config["debs"]:
        installDeb(i["id"], i["url"])


command_switch = {
    "help": help,
    "list": list,
    "install": install,
    "remove": remove,
    "update": update
}

if len(args) > 1:
    command_switch[args[1]]()