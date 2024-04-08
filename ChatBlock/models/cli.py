"""
	intelliQ Command Line Interface
	Basic implementation of the CLI application as described in the req. specification of intelliQ
	Usage: Setup virtual environment and run se2226
	Made with the @click package
"""

import os
import click
import re

import node

import pandas as pd
import requests as http

from io import StringIO
from tabulate import tabulate



@click.group()
def main(ctx, is_boot, n):
    '''ChatBlock command interface'''

    ctx.obj['mynode'] = node.Node('localhost', 5000, is_boot, n)

def validate_address(value):
    """
    Custom type converter function to extract integer value from a string of the format id{int}.
    """
    match = re.match(r'id{(\d+)}', value)
    if match:
        return int(match.group(1))
    else:
        raise click.BadParameter('Invalid format. Expected format: id{int}')

def int_or_string(value):
    """
    Custom type converter function that accepts either a string or an int.
    """
    try:
        # Try converting the value to int
        return int(value)
    except ValueError:
        # If conversion to int fails, return the value as string
        return str(value)

@main.command(short_help='Create a new transaction')
@click.argument('recipient_address', type = validate_address)
@click.argument('message', type = int_or_string)
def t(ctx, recipient_address, message):
    '''Send a message to the recipient address'''
	
    id = recipient_address
    mynode = ctx.obj['mynode']
    if type(message) == int:
        click.echo(f'Sending {message} coins to node {id}.')
        mynode.create_transaction(id, mynode.ring[id]['address'], message, broadcast=True, type_of_transaction='money')
    #else the message is string
    else:
        click.echo(f'Sending \'{message}\' message to node {id}.')
        mynode.create_transaction(id, mynode.ring[id]['address'], message, broadcast=True, type_of_transaction='string')