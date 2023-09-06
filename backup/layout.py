from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel

from textwrap import dedent
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


def update_info(path, total_files, total_size, files, size):
    layout["info"].update(
        dedent(
            f"""\
            [bold]Path:[/bold] {path}
            [bold]Total files:[/bold] {intcomma(files)}/{intcomma(total_files)}
            [bold]Total size:[/bold] {naturalsize(size)}/{naturalsize(total_size)}"""
        )
    )
    return layout


def info_layout(text):
    layout["info"].update("[bold]" + text + "[/bold]")
    return layout


def finish_layout(errors, files, size, cfg):
    layout["info"].update(
        dedent(
            f"""\
            [bold]Backup finished![/bold]

            [bold]Total files:[/bold] {intcomma(files + errors)}
            [bold]Unsucsessfull files:[/bold] {intcomma(errors)}
            [bold]Total size:[/bold] {naturalsize(size)}
            [bold]Time taken:[/bold] {naturaldelta(datetime.now() - cfg['start_time'])}

            A complete log has been written to {cfg['log_path']}."""
        )
    )
    return layout
