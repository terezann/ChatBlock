import os
import click
import re
import pickle
import node
import block

FILEPATH = './mynode'
boot_ip = '192.168.0.3'
boot_port = 5000


@click.group()
@click.option('--reboot', type=bool, default=False, help='Overwrite node')
@click.option('--is_boot', type=bool, default=False, help='Whether the node is bootstrap or not.')
@click.option('--node_ip', default='192.168.0.2', help='Ip address of each node.')
@click.option('--n', type=int, default=5, help='Number of nodes in the network.')
@click.option('--capacity', type=int, default=5, help='Capacity of each block.')
def main(reboot, is_boot, node_ip, n, capacity):
    '''ChatBlock command interface \n
       You need to give is_boot and n options for initialization '''
    print(os.path.exists(FILEPATH))
    if reboot or not os.path.exists(FILEPATH):
        print("Rebooting")
        block.capacity = capacity 
        bootstrap_address = (boot_ip, boot_port)
        mynode = node.Node(node_ip, 5000, bootstrap_address, is_boot, n)
        with open(FILEPATH, 'wb') as file:
            pickle.dump(mynode, file)
        click.echo("Node initialized.")

def get_node_info():
    if os.path.exists(FILEPATH):
        with open(FILEPATH, 'rb') as file:
            return pickle.load(file)
    else:
        click.echo("Node has not been initialized.")
        return

def validate_address(value):
    """
    Custom type converter function to extract integer value from a string of the format id{int}.
    """
    click.echo("Validating recipient address...")

    match = re.match(r'id(\d+)', value)
    if match:
        click.echo("Recipient address validated.")
        return int(match.group(1))
    
    else:
        click.echo("Invalid recipient address format.")
        raise click.BadParameter('Invalid format. Expected format: id{int}')

def int_or_string(value):
    """
    Custom type converter function that accepts either a string or an int.
    """
    click.echo("Converting value to integer or string...")
    try:
        # Try converting the value to int
        result = int(value)
        click.echo("Value converted to integer.")
        return result

    except ValueError:
        # If conversion to int fails, return the value as string
        click.echo("Value is not an integer. Keeping it as string.")
        return str(value)

@main.command(short_help='Create a new transaction')
@click.argument('recipient_address', type = validate_address)
@click.argument('message', type = int_or_string)
def t(recipient_address, message):
    '''Send a message to the recipient address'''
    click.echo("Executing 't' command...")
    id = recipient_address
    mynode:node.Node  = get_node_info()
    if type(message) == int:
        click.echo(f'Sending {message} coins to node {id}.')
        mynode.create_transaction(id, mynode.ring[id]['address'], message, broadcast=True, type_of_transaction='money')
    #else the message is string
    else:
        click.echo(f'Sending \'{message}\' message to node {id}.')
        mynode.create_transaction(id, mynode.ring[id]['address'], message, broadcast=True, type_of_transaction='string')


@main.command(short_help='Set the node stake')
@click.argument('amount', type = int)
def stake(amount):
    '''Set the node's stake'''
    click.echo("Executing 'stake' command...")
    if amount < 0:
        click.echo("Staking amount should be positive.")
        return
    mynode:node.Node  = get_node_info()
    mynode.stake(amount)
    click.echo(f"Setting stake value to {amount}.")


@main.command(short_help='View last validated block')
def view():
    '''View last block in the blockchain'''
    click.echo("Executing 'view' command...")
    mynode:node.Node  = get_node_info()
    mynode.view_block()
    

@main.command(short_help='Show balance')
def balance():
    '''Show current wallet balance'''
    click.echo("Executing 'balance' command...")
    mynode:node.Node  = get_node_info()
    click.echo(f"The current balance is {mynode.balances[mynode.id]}")
    return

if __name__ == '__main__':
    main()