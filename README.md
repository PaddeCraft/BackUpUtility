# BackUpUtility

## What is it?
A simple BackUp-Programm with advanced features,\
like excluding files with specific strings in their path.

## Installation
For installation I recommend [pipx](https://pypa.github.io/pipx/),\
but you can use normal pip too.\
Go to the latest release.\
At the bottom of the release you'll find the pipx installation command.\
To use normal pip, type pip instead of pipx.
<br><br>
To install the newest development version (latest commit),\
type `pipx install https://github.com/PaddeCraft/BackUpUtility/archive/refs/heads/main.zip`

## Usage
```shell
backup                          # Create backup using ui
backup --configfile <FILE>      # Specify the name of the config
                                # file, no other input needed
backup --create-config-file     # Create new config file
backup --version                # Show version and exit
backup --help                   # Show help            
```

## Configuration
The config files are located at `$HOME/.PaddeCraftSoftware/BackUp/config/*.toml`.
Example:
```toml
# Name used in the ui
name = "Testing config"
# Paths that get copied
paths = [
    "/some/example/path/",
    "/some/other/path/"
]
# Exclude filters can be...
excludes = [
    # ...whole paths...
    "/some/example/path/subdirectory/",
    # ...or parts of paths.
    "__pycache__",
    # If one of the excludes is in the file's path, the file will not be copied.
    # You can also filter for file extensions.
    ".tmp"
]

[settings]
# specify if the backup should be in a .zip-file or not
useZip = false
# specify if the last backup made with this configuration should be deleted
deleteLast = true
# The path where the backup should be stored
backupDest = "/run/media/me/my/ssd/"
# The name of the file/folder. Formatted with datetime.datetime.strftime
backupName = "backup-%d-%m-%Y-%H-%M-%S"

# The program stores information about the last backup here
[doNotTouch]
lastBackup = false
lastBackupName = ""
lastBackupTime = 0
```