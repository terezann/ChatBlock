import node
import transaction
import random

def broadcast_transaction(transaction: transaction.Transaction, nodes):
    for node in nodes:
        node.validate_transaction(transaction)

def broadcast_block(n, nodes):
    seed = nodes[0].blockchain[-1].hash
    validator = nodes[0].POS(seed)
    for i in range(0, n):
        if i != validator:
            nodes[i].validate_block(nodes[validator].blockchain[-1])
### Test the app with n nodes

## Suppose that the transactions start after all the nodes are inserted

# Set n
n = 10
nodes = []

# Create the bootstrap node
nodes.append(node.Node(True))
nodes[0].set_id()
nodes[0].register_node(0, 1, nodes[0].wallet['address'], 1000, 5)

# Create genesis block
nodes[0].create_genesis_block(n)

# Insert the nodes
id = 1
while id < n:
    nodes.append(node.Node(False))
    nodes[0].register_node(id, 1, nodes[id].wallet['address'], 1000, 5*id)
    nodes[id].blockchain = nodes[0].blockchain.copy()
    nodes[id].id = id
    id += 1

# Fix stakes, balances, nonces
id = 1
while id < n:
    nodes[id].balances = nodes[0].balances.copy()
    nodes[id].stakes = nodes[0].stakes.copy()
    nodes[id].nonces = nodes[0].nonces.copy()
    nodes[id].ring = nodes[0].ring.copy()

    id += 1


"""
# Node 4 sends 100 to node 5
transaction = nodes[4].create_transaction(nodes[5].wallet['address'], 100)
broadcast_transaction(transaction, nodes)
"""

num = 0
capacity = 5
# Make 5 random transactions
for i in range(9):
    sender_id = random.randint(0, n-1)
    receiver_id = random.randint(0, n-1)
    amount = random.randint(1, 1000)
    # Make sure receiver id is not equal to sender id
    while receiver_id == sender_id:
        receiver_id = random.randint(0, n-1)
    transaction = nodes[sender_id].create_transaction(nodes[receiver_id].wallet['address'], amount)
    broadcast_transaction(transaction, nodes)
    num += 1
    if num == capacity:
        num = 0
        broadcast_block(n, nodes)


print(nodes[0].balances)
print(nodes[3].balances)
print(len(nodes[0].transactions))
print(len(nodes[3].transactions))


# Make an invalid transaction
sender_id = random.randint(0, n-1)
receiver_id = random.randint(0, n-1)
amount = 10000
# Make sure receiver id is not equal to sender id
while receiver_id == sender_id:
    receiver_id = random.randint(0, n-1)
transaction = nodes[sender_id].create_transaction(nodes[receiver_id].wallet['address'], amount)
broadcast_transaction(transaction, nodes)


print(nodes[0].balances)
print(nodes[3].balances)
print(len(nodes[0].transactions))
print(len(nodes[3].transactions))



## Observations
"""
-- The initial transaction from bootstrap to address 0 (1000*n) does not increase bootstrap's nonce

-- Have not tested the validate_chain function

-- See how the id is given to node

-- Change line 39 in node.py

-- We have not made the stakes to be a transaction

-- We have not make the validator to get the fees
"""
