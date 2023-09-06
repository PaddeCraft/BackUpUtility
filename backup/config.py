import os
import toml
import time
from datetime import datetime

from .config_migrations import migrate_config

default_config = {
    "name": "Example config",
    "version": 1,
    "paths": ["/some/example/path", "/some/other/path"],
    "excludes": ["*.tmp", "/some/example/path/to/exclude"],
    "settings": {
        "use_zip": True,
        "zip_compression_level": 0,
        "delete_last": True,
        "backup_dest": "/run/media/someuser/somedisk/backups",
        "backup_name": "backup-%d-%m-%Y-%H-%M-%S",
    },
    "do_not_touch": {
        "last_backup": False,
        "last_backup_name": "",
        "last_backup_time": 0,
    },
}

home_path = os.path.expanduser("~")

software_path = os.path.join(home_path, ".PaddeCraftSoftware", "BackUp")
config_path = os.path.join(software_path, "config")
log_path = os.path.join(software_path, "logs")

os.makedirs(log_path, exist_ok=True)
os.makedirs(config_path, exist_ok=True)


def create_default_config(name, fname):
    with open(
        os.path.join(config_path, fname + ".toml"), "w+", encoding="utf-8"
    ) as conf:
        c = default_config
        c["name"] = name
        toml.dump(c, conf)


def get_configs():
    configs = []
    for file in os.listdir(config_path):
        if file.endswith(".toml"):
            f = os.path.join(config_path, file)
            content = toml.load(f)
            name = content["name"]
            configs.append({"name": name, "file": f})
    return configs


def load_config(file):
    migrate_config(file)

    content = toml.load(file)
    now = datetime.now()
    use_zip = content["settings"]["use_zip"]
    dest = content["settings"]["backup_dest"]
    name = now.strftime(content["settings"]["backup_name"]) + (
        ".zip" if use_zip else ""
    )

    return {
        "paths": content["paths"],
        "excludes": content["excludes"],
        "use_zip": use_zip,
        "zip_compression_level": content["settings"]["zip_compression_level"],
        "delete_last": content["settings"]["delete_last"],
        "backup_dest": dest,
        "backup_name": name,
        "backup_path": os.path.join(dest, name),
        "start_time": now,
        "log_path": os.path.join(log_path, name + ".log"),
        "config_file": file,
        "last_backup": content["do_not_touch"]["last_backup_name"],
        "last_backup_exists": content["do_not_touch"]["last_backup"],
        "last_backup_time": content["do_not_touch"]["last_backup_time"],
    }


def load_from_file_name(fname):
    return load_config(os.path.join(config_path, fname))


def create_last_backup_note(cfg):
    content = toml.load(cfg["config_file"])
    with open(cfg["config_file"], "w", encoding="utf-8") as f:
        content["do_not_touch"]["last_backup"] = True
        content["do_not_touch"]["last_backup_name"] = cfg["backup_path"]
        content["do_not_touch"]["last_backup_time"] = int(time.time())
        toml.dump(content, f)
