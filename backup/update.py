import subprocess
import requests
import sys
import json


def update():
    print("Looking up newest version...")

    try:
        req = requests.get(
            "https://raw.githubusercontent.com/PaddeCraft/BackUpUtility/main/backup/__init__.py"
        )
        ver = req.text.replace('"', "").replace(" ", "").splitlines()[0].split("=")[1]
    except:
        print("Failed to look up version. Check your internet connection.")
        sys.exit(1)

    py = sys.executable
    download_url = (
        f"https://github.com/PaddeCraft/BackUpUtility/archive/refs/tags/{ver}.zip"
    )

    pkgs_pip_cmd = subprocess.run(
        [py, "-m", "pip", "list", "--format=freeze"], capture_output=True, text=True
    )
    pkgs_pipx_cmd = subprocess.run(
        [py, "-m", "pipx", "list", "--json"], capture_output=True, text=True
    )
    if pkgs_pip_cmd.returncode != 0:
        pkgs_pip_cmd = subprocess.run(
            ["pip", "list", "--format=freeze"], capture_output=True, text=True
        )
        if pkgs_pip_cmd.returncode != 0:
            pkgs_pip_cmd = subprocess.run(
                ["pip3", "list", "--format=freeze"], capture_output=True, text=True
            )
    if pkgs_pipx_cmd.returncode != 0:
        pkgs_pipx_cmd = subprocess.run(
            ["pipx", "list", "--json"], capture_output=True, text=True
        )

    pkgs_pip = []
    pkgs_pipx = []

    print("Parsing current packages...")

    for p in pkgs_pip_cmd.stdout.splitlines():
        pkgs_pip.append({"name": p.split("==")[0], "version": p.split("==")[1]})

    for _, pkg in json.loads(pkgs_pipx_cmd.stdout)["venvs"].items():
        pkgs_pipx.append(
            {
                "name": pkg["metadata"]["main_package"]["package"],
                "version": pkg["metadata"]["main_package"]["package_version"],
            }
        )

    backup_pip = [p for p in pkgs_pip if p["name"] == "BackUp"]

    if len(backup_pip) != 0:
        if backup_pip[0]["version"] != ver:
            print("Updating BackUpUtility using pip...")
            p = subprocess.run(
                [py, "-m", "pip", "install", download_url], stdout=subprocess.DEVNULL
            )
            if p.returncode != 0:
                p = subprocess.run(
                    ["pip", "install", download_url], stdout=subprocess.DEVNULL
                )
                if p.returncode != 0:
                    p = subprocess.run(
                        ["pip3", "install", download_url], stdout=subprocess.DEVNULL
                    )

    backup_pipx = [p for p in pkgs_pipx if p["name"] == "BackUp"]

    if len(backup_pipx) != 0:
        if backup_pipx[0]["version"] != ver:
            print("Updating BackUpUtility using pipx...")
            p = subprocess.run(
                [py, "-m", "pipx", "install", download_url, "--force"],
                stdout=subprocess.DEVNULL,
            )
            if p.returncode != 0:
                p = subprocess.run(
                    ["pipx", "install", download_url, "--force"],
                    stdout=subprocess.DEVNULL,
                )

    print("PaddeCraft's BackUpUtility is up to date!")
