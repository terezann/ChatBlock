import blockchain
from transaction import Transaction
import wallet
import datetime as date

from collections import OrderedDict
from Crypto.Hash import SHA

capacity = 5

class Block:
    def __init__(self, index, validator, previous_hash, transactions):
        ##set
        self.index = index
        #self.previousHash
        self.previous_hash = previous_hash
        #self.timestamp
        self.timestamp = date.datetime.now() 
        #self.listofTransactions
        self.list_of_transactions = transactions
        self.validator = validator
        self.capacity = capacity
        self.hash = self.myHash()
        

    def to_dict(self):
        return OrderedDict({
            'index': self.index,
            'previous_hash': self.previous_hash,
            'validator': self.validator,
            'capacity': self.capacity,
            'list_of_transactions': self.list_of_transactions
            })

    def myHash(self):
        #calculate self.hash
        return SHA.new(str(self.to_dict).encode("utf-8")).hexdigest()
    
    def __reduce__(self):
        return (self.__class__, (self.index, self.validator, self.previous_hash, self.list_of_transactions))

    # def add_transaction(self, transaction): #add a blockchain parameter
    #     #add a transaction to the block
    #     if len(self.list_of_transactions) == capacity:
    #         print("the max capacity is reached: ", capacity)
    #         return
    #     self.list_of_transactions.append(transaction)
    #     if len(self.list_of_transactions) == capacity:
    #         self.myHash()

    