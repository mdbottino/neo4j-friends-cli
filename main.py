from dotenv import load_dotenv 
load_dotenv()

import click
from model import Graph


@click.group()
def cli():
    pass


@cli.command()
@click.argument('name')
@click.argument('age')
def add(name, age):
    added = Graph.add(name, age)
    if added:
        click.echo(f'Created new Person: {name} ({age})')


@cli.command()
@click.argument('name')
def remove(name):
    removed = Graph.remove(name)
    if removed:
        click.echo(f'Removed {name}')


@cli.command()
@click.argument('name')
@click.argument('age')
def edit(name, age):
    edited = Graph.edit(name, age)
    if edited:
        click.echo(f'Edited {name} successfully, now is {age} years old.')


@cli.command()
def info():
    result = Graph.info()
    click.echo(f'Found {result["n"]} Nodes and {result["r"]} Relationships')


@cli.command()
@click.argument('name')
@click.argument('friend')
def befriend(name, friend):
    ok = Graph.befriend(name, friend)
    success_msg = f'{name} and {friend} are now friends!'
    error_msg = 'No relationship created'
    click.echo(success_msg if ok else error_msg)


@cli.command('list')
@click.argument('name')
@click.option('--depth', default=1)
@click.option('--full', default=False, is_flag=True)
def list_friends(name, depth, full):
    friends = Graph.list_friends(name, depth, full)
    for friend in friends:
        age = f' ({friend["age"]})' if friend["age"] else ''
        click.echo(f'{friend["name"]}{age}')


if __name__ == '__main__':
    cli()