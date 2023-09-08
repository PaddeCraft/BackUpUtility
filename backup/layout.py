from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich import print

from textwrap import dedent
from humanize import naturalsize, intcomma, naturaldelta, precisedelta

from datetime import datetime, timedelta

layout = Layout()

layout.split_column(
    Layout(Panel("[bold]PaddeCraft's Backup Utility[/bold]"), name="title"),
    Layout(" ", name="spacer"),
    Layout(name="info"),
    Layout(" ", name="spacer2"),
    Layout(" ", name="progress"),
)

layout["title"].size = 3
layout["spacer"].size = 1
layout["spacer2"].size = 1
layout["progress"].size = 1


def update_info(path, total_files, total_size, files, size, rate, file_size):
    if rate == 0:
        rate = 1

    completion_time = datetime.now() + timedelta(seconds=file_size / rate)

    layout["info"].update(
        dedent(
            f"""\
            [bold]Path:[/bold] '{path}'
            [bold]Total files:[/bold] {intcomma(files)}/{intcomma(total_files)}
            [bold]Total size:[/bold] {naturalsize(size)}/{naturalsize(total_size)}
            
            [bold]Speed:[/bold] {naturalsize(rate)}/Second
            
            At this rate, this file ({naturalsize(file_size)}) is expected to be completed in a total time of {precisedelta(completion_time)}.
            This time will have passed at {completion_time.strftime("%d[bold white].[/bold white]%m[bold white].[/bold white]%Y %H:%M:%S")}.
            """
        )
    )
    return layout


def info_layout(text):
    layout["info"].update("[bold]" + text + "[/bold]")
    return layout


def finish_msg(errors, files, size, cfg):
    print(
        dedent(
            f"""\n
            [bold]Backup finished![/bold]

            [bold]Total files:[/bold] {intcomma(files + errors)}
            [bold]Unsucsessfull files:[/bold] {intcomma(errors)}
            [bold]Total size:[/bold] {naturalsize(size)}
            [bold]Time taken:[/bold] {naturaldelta(datetime.now() - cfg['start_time'])}

            A complete log has been written to {cfg['log_path']}."""
        )
    )
    return layout
