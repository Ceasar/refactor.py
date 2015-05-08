import click

import refactor


@click.command()
@click.argument('filename')
@click.argument('name')
def move_node(filename, name):
    with open(filename) as fp:
        click.echo(refactor.move_node(fp, name))


@click.group()
def cli():
    pass

cli.add_command(move_node)
