import json
import os
import os.path as path
import shutil
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


def getVersionFromDebInfo(info: str):
    lines = info.replace("\\n", "\n").split("\n")
    versionStr = "0.0.0"
    version: [int] = []
    for i in lines:
        if i.startswith("Version: "):
            i = i.replace("Version: ", "")
            versionStr = i
            break

    for i in versionStr.split("."):
        version.append(int(i))

    return version


def updateAvailable(old: [int], new: [int]):
    available = False

    for i in range(0, len(old)):
        if new[i] > old[i]:
            available = True
            break

    return available


def prettifyVersion(version):
    string = ""
    for i in version:
        string += str(i) + "."

    return string[:len(string) - 1]


def installDeb(id, url, install):
    fileName = id + ".deb"
    print("Downloading " + fileName)
    subprocess.run(["curl", "--url", url, "-s", "-L", "-J",
                    "-o", fileName, "--next"
                    ], cwd=CacheFolder)
    print("Done")
    if install:
        print("Installing " + fileName)
        subprocess.run(["sudo", "dpkg", "-i", fileName], cwd=CacheFolder)
        print("Done")
    else:
        print("Extracting version from " + fileName)
        subprocess.run(["ar", "x", fileName], cwd=CacheFolder)
        subprocess.run(["tar", "-f", "control.tar.gz", "-x"], cwd=CacheFolder)
        infoFile = open(path.join(CacheFolder, "control"), 'r')
        infoFileContent = str(infoFile.read())
        downloadedVersion = getVersionFromDebInfo(infoFileContent)
        installedInfoFile = subprocess.run(["dpkg", "--status", id], stdout=subprocess.PIPE).stdout
        installedVersion = getVersionFromDebInfo(str(installedInfoFile)[2:])

        shouldUpdate = updateAvailable(installedVersion, downloadedVersion)
        if shouldUpdate:
            print("A new version is available (" + prettifyVersion(downloadedVersion)
                  + "), current version is " + prettifyVersion(installedVersion))
            choice = input("Install? [Y/n] ")
            if not (choice.lower() == "n"):
                print("Installing " + fileName)
                subprocess.run(["sudo", "dpkg", "-i", fileName], cwd=CacheFolder)
                print("Done")
        else:
            print("Up to date")
    print("Cleaning cache")
    folder = CacheFolder
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
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
        installDeb(deb_id, deb_url, True)
        writeConfig()
    else:
        print("Not enough arguments!")


def remove():
    print("remove")


def update():
    print("Upgrading not-ppa-debs:")
    global config
    for i in range(0, len(config["debs"])):
        entry = config["debs"][i]
        print("[" + str(i + 1) + "/" + str(len(config["debs"])) + "] Checking updates for " + entry["id"])
        installDeb(entry["id"], entry["url"], False)


command_switch = {
    "help": help,
    "list": list,
    "install": install,
    "remove": remove,
    "update": update
}

if len(args) > 1:
    command_switch[args[1]]()
