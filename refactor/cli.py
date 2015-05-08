import ast
import pprint

import click

import refactor
import visualize


@click.command()
@click.argument('filename')
@click.argument('names', nargs=-1)
def move_nodes(filename, names):
    with open(filename) as fp:
        click.echo(refactor.move_nodes(ast.parse(fp.read()), names, fp.name))


@click.command()
@click.argument('filename')
@click.option('--draw', is_flag=True)
def show_dependencies(filename, draw):
    with open(filename) as fp:
        deps = refactor.get_dependencies(ast.parse(fp.read()))
    if draw:
        visualize.draw(deps)
    else:
        click.echo(pprint.pformat(deps))


@click.group()
def cli():
    pass

cli.add_command(move_nodes)
cli.add_command(show_dependencies)
