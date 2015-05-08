import ast
import pprint

import click

import refactor


@click.command()
@click.argument('filename')
@click.argument('name')
def move_node(filename, name):
    with open(filename) as fp:
        click.echo(refactor.move_node(fp, name))


@click.command()
@click.argument('filename')
def list_dependencies(filename):
    with open(filename) as fp:
        deps = refactor.get_dependencies(ast.parse(fp.read()))
    click.echo(pprint.pformat(deps))


@click.group()
def cli():
    pass

cli.add_command(move_node)
cli.add_command(list_dependencies)
