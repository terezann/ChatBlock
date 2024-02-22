from collections import OrderedDict

import binascii

import Crypto
import Crypto.random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import requests
from flask import Flask, jsonify, request, render_template

class Transaction:

    def __init__(self, sender_address, sender_private_key, receiver_address, value):

        #set

        #self.sender_address: Το public key του wallet από το οποίο προέρχονται τα χρήματα
        #self.receiver_address: Το public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        #self.amount: Το ποσό που θα μεταφερθεί
        #self.transaction_id: Το hash του transaction
        #selfSignature με το private key

    def to_dict(self):

    def sign_transaction(self):
        #sign transaction with private key

