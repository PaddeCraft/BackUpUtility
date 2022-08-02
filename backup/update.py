import subprocess
import requests
import sys
import json


def update():
    print("Looking up newest version...")

    try:
        req = requests.get(
            "https://raw.githubusercontent.com/PaddeCraft/BackUpUtility/main/backup/__init__.py")
        ver = req.text.replace('"', "").replace(
            " ", "").splitlines()[0].split("=")[1]
    except:
        print("Failed to look up version. Check your internet connection.")
        sys.exit(1)

    py = sys.executable
    downloadUrl = f"https://github.com/PaddeCraft/BackUpUtility/archive/refs/tags/{ver}.zip"

    pkgsPipCmd = subprocess.run([py, "-m", "pip", "list", "--format=freeze"],
                                capture_output=True, text=True)
    pkgsPipxCmd = subprocess.run([py, "-m", "pipx", "list", "--json"],
                                 capture_output=True, text=True)

    pkgsPip = []
    pkgsPipx = []

    print("Parsing current packages...")

    for p in pkgsPipCmd.stdout.splitlines():
        pkgsPip.append({
            "name": p.split("==")[0],
            "version": p.split("==")[1]
        })

    for _, pkg in json.loads(pkgsPipxCmd.stdout)["venvs"].items():
        pkgsPipx.append({
            "name": pkg["metadata"]["main_package"]["package"],
            "version": pkg["metadata"]["main_package"]["package_version"],
        })

    backUpPip = [p for p in pkgsPip if p["name"] == "BackUp"]

    if len(backUpPip) != 0:
        if backUpPip[0]["version"] != ver:
            print("Updating BackUpUtility using pip...")
            subprocess.run([py, "-m", "pip", "install", downloadUrl],
                           stdout=subprocess.DEVNULL)

    backUpPipx = [p for p in pkgsPipx if p["name"] == "BackUp"]

    if len(backUpPipx) != 0:
        if backUpPipx[0]["version"] != ver:
            print("Updating BackUpUtility using pipx...")
            subprocess.run([py, "-m", "pipx", "install", downloadUrl],
                           stdout=subprocess.DEVNULL)

    print("PaddeCraft's BackUpUtility is up to date!")
