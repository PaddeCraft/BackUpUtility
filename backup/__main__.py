import zipfile
from typer import Typer

import os
import zipfile
import shutil

from rich.progress import Progress

from backup.config import *
from backup.update import update
from backup.log import configure, log
from backup.layout import updateInfo, terminal, infoLayout, finishLayout

from backup.__init__ import VERSION

from InquirerPy.validator import EmptyInputValidator
from InquirerPy import prompt

app = Typer()

totalFiles = 0
totalSize = 0
errorFiles = 0
files = 0
size = 0

dayEndings = {
    1: 'st',
    2: 'nd',
    3: 'rd',
    21: 'st',
    22: 'nd',
    23: 'rd',
    31: 'st'
}


def timeSuffix(day):
    try:
        return dayEndings[day]
    except KeyError:
        return 'th'


def iterateFiles(pathList, excludeList):
    for path in pathList:
        for root, _, files in os.walk(path):
            for file in files:
                include = True
                for exclude in excludeList:
                    if exclude.replace("\\", "/") in os.path.join(root, file).replace("\\", "/"):
                        include = False
                if include:
                    yield {
                        "src": os.path.join(root, file),
                        "relative": file,
                        "main": path,
                        "mainLength": len(path),
                    }


@app.command()
def backup(configFileName: str = None, create_config: bool = False, version: bool = False, update: bool = False):
    global totalFiles, totalSize, files, size, errorFiles
    if version:
        print("PaddeCraft's Backup Utility v" + VERSION)
        print("Copyright (C) PaddeCraft")
        exit(0)
    if update:
        update()
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
        createDefaultConfig(result[0], filename)
        print("Configuration created.")
        exit(0)
    if configFileName is None:
        cfgs = getConfigs()
        if len(cfgs) == 0:
            print("No config files found.")
            print("You can create a new one with the --create-config flag.")
            exit(1)
        if len(cfgs) == 1:
            cfg = loadConfig(cfgs[0]["file"])
        else:
            result = prompt(
                [{
                    "type": "list",
                    "message": "Select a backup configuration",
                    "choices": [cfg['name'] for cfg in cfgs]
                }], style={"questionmark": "#ff9d00 bold"},
            )
            for c in cfgs:
                if c['name'] == result[0]:
                    cfg = loadConfig(c['file'])
                    break
    else:
        cfg = loadFromFileName(configFileName)

    t = datetime.utcfromtimestamp(
        cfg["lastBackupTime"])
    print("Fun fact: Your last backup with this configuration was started on " +
          t.strftime(
              f'%A, the %-d{timeSuffix(int(t.strftime("%-d")))} %B %Y at %H:%M:%S.'
          )
          )
    time.sleep(8)

    # Configure logging
    configure(cfg)
    with Progress(console=terminal) as progress:
        # Progress bar with no status for indicating the deleting
        progress.log(infoLayout("Deleting last backup..."))
        deletingBar = progress.add_task(
            "[bold]Deleting last backup [/bold] ", total=None)

        # Delete last backup if the user wants to
        if cfg["lastBackup"] and cfg["lastBackupExists"]:
            try:
                if os.path.isfile(cfg["lastBackup"]):
                    os.remove(cfg["lastBackup"])
                else:
                    shutil.rmtree(cfg["lastBackup"])
            except Exception as e:
                log(f"Error deleting last backup: {str(e)}", error=True)

        progress.update(deletingBar, visible=False)
        progress.log(infoLayout("Indexing directories..."))
        indexingBar = progress.add_task(
            "[bold]Calculating space requirements [/bold] ", total=None)

        # Check total size and files
        for f in iterateFiles(cfg["paths"], cfg["excludes"]):
            if os.access(f["src"], os.R_OK):
                totalFiles += 1
                totalSize += os.path.getsize(f["src"])
            else:
                errorFiles += 1
        if totalSize > shutil.disk_usage(cfg["backupDest"])[2]:
            questions = [
                {"message": "Not enough space aviable. Try anyways?",
                 "type": "confirm", "default": False},
            ]
            result = prompt(questions, style={"questionmark": "#ff9d00 bold"},)
            if not result[0]:
                exit(0)

        # Create note that the last backup has been created
        createLastBackupNote(cfg)

        # Progress bar for indicating the backup phase
        progress.update(indexingBar, visible=False)
        backupBar = progress.add_task(
            "[bold]Backing files up [/bold]", total=totalSize)

        # Open the zip file
        if cfg["useZip"]:
            zip = zipfile.ZipFile(
                cfg["backupPath"],
                "a",
                strict_timestamps=False,
                compression=zipfile.ZIP_DEFLATED,
            )

        # The backup phase
        for f in iterateFiles(cfg["paths"], cfg["excludes"]):
            if os.access(f["src"], os.R_OK):
                files += 1
                sz = os.path.getsize(f["src"])
                size += sz
                progress.log(updateInfo(
                    f["src"], totalFiles, totalSize, files, size))
                try:
                    if cfg["useZip"]:
                        zip.write(f["src"], f["src"][f["mainLength"]:])
                    else:
                        relPth = "/".join(
                            f["src"].replace(
                                f["main"], ""
                            ).replace(
                                "\\", "/"
                            ).split("/")[:-1])
                        try:
                            if relPth[0] == "/":
                                relPth = relPth[1:]
                        except:
                            pass
                        mainDir = f["main"]
                        if mainDir[-1] == "/":
                            mainDir = mainDir[:-1]
                        mainDir = mainDir.replace("\\", "/").split("/")[-1]
                        folder = os.path.join(
                            cfg["backupDest"],
                            cfg["backupName"],
                            mainDir,
                            relPth,
                        )
                        os.makedirs(folder, exist_ok=True)
                        shutil.copy2(f["src"], os.path.join(
                            folder, f["src"].split("/")[-1]))
                    log(f"Added {f['src']} to backup.")
                except Exception as e:
                    log(f"Error while backing up {f['src']}: {str(e)}", error=True)
                progress.update(backupBar, advance=sz)
            else:
                log(f"Error: {f['src']} is not readable.", error=True)

        # Close the zip file if it was used
        if cfg["useZip"]:
            zip.close()
        progress.log(finishLayout(errorFiles, files, size, cfg))
        log(f"""\n
          Backup finished.
          {errorFiles} files could not be backed up.
          {files} files were backed up.
          {size} bytes were backed up.""")
