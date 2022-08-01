import os
import toml
import time
from datetime import datetime

defaultConfig = {
    'name': 'Example config',
    'paths': [
        '/some/example/path',
        '/some/other/path'
    ],
    'excludes': [
        '*.tmp',
        '/some/example/path/to/exclude'
    ],
    'settings': {
        'useZip': True,
        'deleteLast': True,
        'backupDest': '/run/media/someuser/somedisk/backups',
        'backupName': 'backup-%d-%m-%Y-%H-%M-%S',
    }, 'doNotTouch': {
        'lastBackup': False,
        'lastBackupName': '',
        'lastBackupTime': 0,
    }
}

userPath = os.path.expanduser("~")

softwarePath = os.path.join(
    userPath, ".PaddeCraftSoftware", "BackUp")
configPath = os.path.join(softwarePath, "config")
logPath = os.path.join(softwarePath, "logs")

os.makedirs(logPath, exist_ok=True)
os.makedirs(configPath, exist_ok=True)


def createDefaultConfig(name, fname):
    with open(os.path.join(configPath, fname + ".toml"), 'w+', encoding="utf-8") as conf:
        c = defaultConfig
        c['name'] = name
        toml.dump(c, conf)


def getConfigs():
    configs = []
    for file in os.listdir(configPath):
        if file.endswith(".toml"):
            f = os.path.join(configPath, file)
            content = toml.load(f)
            name = content['name']
            configs.append({'name': name, 'file': f})
    return configs


def loadConfig(file):
    content = toml.load(file)
    now = datetime.now()
    useZip = content['settings']['useZip']
    dest = content['settings']['backupDest']
    name = now.strftime(content['settings']
                        ['backupName']) + (".zip" if useZip else "")
    return {
        'paths': content['paths'],
        'excludes': content['excludes'],
        'useZip': useZip,
        'deleteLast': content['settings']['deleteLast'],
        'backupDest': dest,
        'backupName': name,
        'backupPath': os.path.join(dest, name),
        'startTime': now,
        'logPath': os.path.join(logPath, name + ".log"),
        'configFile': file,
        'lastBackup': content['doNotTouch']['lastBackupName'],
        'lastBackupExists': content['doNotTouch']['lastBackup'],
        'lastBackupTime': content['doNotTouch']['lastBackupTime']
    }


def loadFromFileName(fileName):
    return loadConfig(os.path.join(configPath, fileName))


def createLastBackupNote(cfg):
    content = toml.load(cfg["configFile"])
    with open(cfg["configFile"], 'w', encoding="utf-8") as f:
        content['doNotTouch']['lastBackup'] = True
        content['doNotTouch']['lastBackupName'] = cfg['backupPath']
        content['doNotTouch']['lastBackupTime'] = int(time.time())
        toml.dump(content, f)
