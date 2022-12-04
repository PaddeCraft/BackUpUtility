from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel

from humanize import naturalsize, intcomma, naturaldelta

from datetime import datetime

layout = Layout()

terminal = Console()

layout.split_column(
    Layout(" ", name="spacer2"),
    Layout(Panel("[bold]PaddeCraft's Backup Utility[/bold]"), name="title"),
    Layout(" ", name="spacer"),
    Layout(name="info"),
)

layout["title"].size = 3
layout["spacer"].size = 1
layout["spacer2"].size = 2


def updateInfo(path, totalFiles, totalSize, files, size):
    layout["info"].update(
        f"""\
    [bold]Path:[/bold] {path}
    [bold]Total files:[/bold] {intcomma(files)}/{intcomma(totalFiles)}
    [bold]Total size:[/bold] {naturalsize(size)}/{naturalsize(totalSize)}"""
    )
    return layout


def infoLayout(text):
    layout["info"].update("[bold]" + text + "[/bold]")
    return layout


def finishLayout(errors, files, size, cfg):
    layout["info"].update(
        f"""\
        [bold]Backup finished![/bold]
        
        [bold]Total files:[/bold] {intcomma(files + errors)}
        [bold]Unsucsessfull files:[/bold] {intcomma(errors)}
        [bold]Total size:[/bold] {naturalsize(size)}
        [bold]Time taken:[/bold] {naturaldelta(datetime.now() - cfg['startTime'])}
        
        A complete log has been written to {cfg['logPath']}."""
    )
    return layout
