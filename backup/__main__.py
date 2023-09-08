import zipfile
from typer import Typer

import os
import stat
import zipfile
import shutil

from rich.progress import Progress

from backup.config import *
from backup.update import update as update_app
from backup.log import configure, log
from backup.layout import Live, update_info, info_layout, finish_msg, layout

from backup.__init__ import VERSION

from InquirerPy.validator import EmptyInputValidator
from InquirerPy import prompt

app = Typer()

total_files = 0
total_size = 0
error_files = 0
files = 0
size = 0


def time_suffix(day):
    # https://stackoverflow.com/a/5891598
    return {1: "st", 2: "nd", 3: "rd"}.get(day % 20, "th")


def iterate_files(path_list, exclude_list):
    for path in path_list:
        for root, _, files in os.walk(path):
            for file in files:
                include = True
                merged = os.path.join(root, file)

                for exclude in exclude_list:
                    if exclude.replace("\\", "/") in merged.replace("\\", "/"):
                        include = False

                try:
                    if stat.S_ISFIFO(os.stat(merged).st_mode):
                        include = False
                except Exception:
                    include = False

                if merged.startswith("/dev"):
                    include = False

                if include:
                    yield {
                        "src": merged,
                        "relative": file,
                        "main": path,
                        "main_length": len(path),
                    }


@app.command()
def backup(
    config_file_name: str = None,
    create_config: bool = False,
    version: bool = False,
    update: bool = False,
):
    global total_files, total_size, files, size, error_files

    # ---------------------------------------------------------------------------- #
    #                                 Sub-Commands                                 #
    # ---------------------------------------------------------------------------- #
    if version:
        print("PaddeCraft's Backup Utility v" + VERSION)
        print("Copyright (C) PaddeCraft")
        exit(0)

    if update:
        update_app()
        exit(0)

    if create_config:
        questions = [
            {
                "type": "input",
                "message": "Enter a name for your configuration: ",
                "validate": EmptyInputValidator(),
            }
        ]
        result = prompt(questions, style={"questionmark": "#ff9d00 bold"})
        filename = result[0].lower().replace(" ", "_")
        create_default_config(result[0], filename)
        print("Configuration created.")
        exit(0)

    # ---------------------------------------------------------------------------- #
    #                                Config loading                                #
    # ---------------------------------------------------------------------------- #
    if config_file_name is None:
        existing_configs = get_configs()
        if len(existing_configs) == 0:
            print("No config files found.")
            print("You can create a new one with the --create-config flag.")
            exit(1)
        if len(existing_configs) == 1:
            cfg = load_config(existing_configs[0]["file"])
        else:
            result = prompt(
                [
                    {
                        "type": "list",
                        "message": "Select a backup configuration",
                        "choices": [cfg["name"] for cfg in existing_configs],
                    }
                ],
                style={"questionmark": "#ff9d00 bold"},
            )
            for c in existing_configs:
                if c["name"] == result[0]:
                    cfg = load_config(c["file"])
                    break
    else:
        cfg = load_from_file_name(config_file_name)

    t = datetime.utcfromtimestamp(cfg["last_backup_time"])
    print(
        "Fun fact: Your last backup with this configuration was started on "
        + t.strftime(
            f'%A, the %-d{time_suffix(int(t.strftime("%-d")))} %B %Y at %H:%M:%S.'
        )
    )
    time.sleep(5)

    # ---------------------------------------------------------------------------- #
    #                                Initialisation                                #
    # ---------------------------------------------------------------------------- #
    configure(cfg)
    progress = Progress()

    layout["progress"].update(progress)

    # ---------------------------------------------------------------------------- #
    #                                   Main code                                  #
    # ---------------------------------------------------------------------------- #
    with Live(layout, refresh_per_second=15, screen=True):
        # Progress bar with no status for indicating the deleting
        info_layout("Deleting last backup...")
        deleting_bar = progress.add_task(
            "[bold]Deleting last backup [/bold] ", total=None
        )

        # Delete last backup if the user wants to
        if cfg["last_backup"] and cfg["last_backup_exists"] and cfg["delete_last"]:
            try:
                if os.path.isfile(cfg["last_backup"]):
                    os.remove(cfg["last_backup"])
                else:
                    shutil.rmtree(cfg["last_backup"])
            except Exception as e:
                log(f"Error deleting last backup: {str(e)}", error=True)

        progress.update(deleting_bar, visible=False)
        info_layout("Indexing directories...")
        indexing_bar = progress.add_task(
            "[bold]Calculating space requirements [/bold] ", total=None
        )

        # Check total size and files
        for f in iterate_files(cfg["paths"], cfg["excludes"]):
            if os.access(f["src"], os.R_OK):
                total_files += 1
                total_size += os.path.getsize(f["src"])
            else:
                error_files += 1
        if total_size > shutil.disk_usage(cfg["backup_dest"])[2]:
            questions = [
                {
                    "message": "It is possible that the destination has less space available than needed. If you are using compression, the space may be sufficient. Try anyways?",
                    "type": "confirm",
                    "default": False,
                },
            ]
            result = prompt(
                questions,
                style={"questionmark": "#ff9d00 bold"},
            )
            if not result[0]:
                exit(0)

        # Create note that the last backup has been created
        create_last_backup_note(cfg)

        # Progress bar for indicating the backup phase
        progress.update(indexing_bar, visible=False)
        backupBar = progress.add_task(
            "[bold]Backing files up [/bold]", total=total_size
        )

        # Open the zip file
        if cfg["use_zip"]:
            comp_level = cfg["zip_compression_level"]
            if comp_level == 0:
                comp_type = zipfile.ZIP_STORED
            elif comp_level in range(1, 10):  # 1 <= level <= 9
                comp_type = zipfile.ZIP_BZIP2
            else:
                comp_type = zipfile.ZIP_LZMA

            zip = zipfile.ZipFile(
                cfg["backup_path"],
                "a",
                strict_timestamps=False,
                compression=comp_type,
                compresslevel=comp_level,
            )

        backup_start = time.time()

        # The backup phase
        for f in iterate_files(cfg["paths"], cfg["excludes"]):
            if not os.access(f["src"], os.R_OK):
                log(f"Error: {f['src']} is not readable.", error=True)
                continue

            # Rate, in bytes/s
            rate = size / (time.time() - backup_start)

            files += 1
            sz = os.path.getsize(f["src"])
            size += sz

            update_info(f["src"], total_files, total_size, files, size, rate, sz)
            try:
                if cfg["use_zip"]:
                    zip.write(f["src"], f["src"][f["main_length"] :])
                else:
                    rel_pth = "/".join(
                        f["src"]
                        .replace(f["main"], "")
                        .replace("\\", "/")
                        .split("/")[:-1]
                    )
                    try:
                        if rel_pth[0] == "/":
                            rel_pth = rel_pth[1:]
                    except:
                        pass
                    main_dir = f["main"]
                    if main_dir[-1] == "/":
                        main_dir = main_dir[:-1]
                    main_dir = main_dir.replace("\\", "/").split("/")[-1]
                    folder = os.path.join(
                        cfg["backup_dest"],
                        cfg["backup_name"],
                        main_dir,
                        rel_pth,
                    )
                    os.makedirs(folder, exist_ok=True)
                    shutil.copy2(
                        f["src"], os.path.join(folder, f["src"].split("/")[-1])
                    )
                log(f"Added {f['src']} to backup.")
            except Exception as e:
                log(f"Error while backing up {f['src']}: {str(e)}", error=True)
                error_files += 1
            progress.update(backupBar, advance=sz)

    # Close the zip file if it was used
    if cfg["use_zip"]:
        zip.close()

    # Completion messages
    finish_msg(error_files, files, size, cfg)
    log(
        f"""\n
      Backup finished.
      {error_files} files could not be backed up.
      {files} files were backed up.
      {size} bytes were backed up."""
    )
