CONFIG_VERSION_MIGRATIONS = [
    {
        "version": 1,  # Version is the version of the config after migration
        "actions": [
            # Settings
            {"action": "rename", "from": "settings.useZip", "to": "settings.use_zip"},
            {
                "action": "rename",
                "from": "settings.deleteLast",
                "to": "settings.delete_last",
            },
            {
                "action": "rename",
                "from": "settings.backupDest",
                "to": "settings.backup_dest",
            },
            {
                "action": "rename",
                "from": "settings.backupName",
                "to": "settings.backup_name",
            },
            {"action": "create", "key": "settings.zip_compression_level", "value": 0},
            # Do not touch
            {"action": "rename", "from": "doNotTouch", "to": "do_not_touch"},
            {
                "action": "rename",
                "from": "do_not_touch.lastBackup",
                "to": "do_not_touch.last_backup",
            },
            {
                "action": "rename",
                "from": "do_not_touch.lastBackupName",
                "to": "do_not_touch.last_backup_name",
            },
            {
                "action": "rename",
                "from": "do_not_touch.lastBackupTime",
                "to": "do_not_touch.last_backup_time",
            },
        ],
    }
]

import toml


def resolve_parent_key(config, path):
    paths = path.split(".")
    final_key = paths[-1]
    paths.pop(-1)

    data = config
    for pth in paths:
        if not pth in data:
            data[pth] = {}
        data = data[pth]

    return data, final_key


def pop_key(config, path):
    data, final_key = resolve_parent_key(config, path)

    ret = data[final_key]
    del data[final_key]
    return ret


def insert_key(config, path, data):
    _data, final_key = resolve_parent_key(config, path)
    _data[final_key] = data


def migrate_config(fname):
    config = toml.load(fname)
    version = 0
    if "version" in config:
        version = config["version"]

    latest_version = CONFIG_VERSION_MIGRATIONS[-1]["version"]

    if version == latest_version:
        return

    migration_count = 0
    migration_log = ""
    for migration in CONFIG_VERSION_MIGRATIONS:
        if not migration["version"] > version:
            continue

        for action in migration["actions"]:
            _action = action["action"]

            # No case statement in favour of python <3.10 support
            if _action == "rename":
                data = pop_key(config, action["from"])
                insert_key(config, action["to"], data)

            elif _action == "create":
                insert_key(config, action["key"], action["value"])

            elif _action == "delete":
                pop_key(config, action["key"])

            migration_log += (
                " ".join([f"{k.upper()}={v}" for k, v in action.items()]) + "\n"
            )

        migration_count += 1

    config["version"] = latest_version
    print(
        f"Your configuration was {migration_count} version{'s' if migration_count > 1 else ''} behind ({version}=>{latest_version}). It was automatically migrated."
    )
    print("Migration log:")
    print(migration_log, end="\n\n")

    with open(fname, "w", encoding="utf-8") as f:
        toml.dump(config, f)
