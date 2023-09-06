# BackUpUtility

## What is it?
A simple BackUp-Programm with advanced features, like excluding files with specific strings in their path, configurable archive compression, and much more.

## Installation
For installation I recommend [pipx](https://pypa.github.io/pipx/), but you can use normal pip too.

- Go to the latest release.
- At the bottom of the release you'll find the pipx installation command. To use normal pip, type pip instead of pipx.

### Development version
To install the newest development version (latest commit),\
type `pipx install https://github.com/PaddeCraft/BackUpUtility/archive/refs/heads/main.zip`

## Usage
```shell
backup                              # Create backup using ui
backup --config-file-name <FILE>    # Specify the name of the config
                                    # file, no other input needed
backup --create-config-file         # Create new config file
backup --version                    # Show version and exit
backup --update                     # Update pip and/or pipx package
                                    # if an update is aviable
backup --help                       # Show help            
```

## Configuration
The config files are located at `$HOME/.PaddeCraftSoftware/BackUp/config/*.toml`.
Example:
```toml
# Name used in the ui
name = "Testing config"
# Config file version
version = 1
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
] # The filters are checked by 'if exclude in path'

[settings]
# Specify if the backup should be in a .zip-file or not
use_zip = false
# If use_zip is set to true, specify the compression level. Accepted are
#  - The numbers 1-9 (bz2), where 9 produces the highest compression ratio
#  - The numbers >=10, compression using the LZMA algorithm
#  - The number 0, to disable compression
zip_compression_level = 0
# Specify if the last backup made with this configuration should be deleted
delete_last = true
# The path where the backup should be stored
backup_dest = "/run/media/me/my/ssd/"
# The name of the file/folder. Formatted with datetime.datetime.strftime
backup_name = "backup-%d-%m-%Y-%H-%M-%S"

# The program stores information about the last backup here
[do_not_touch]
last_backup = false
last_backup_name = ""
last_backup_time = 0
```

## Development

The project manages dependencies using poetry. To install all of the dependencies, type `poetry install`.