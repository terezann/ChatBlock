from binascii import hexlify, unhexlify
from collections import OrderedDict

from Crypto import Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5


class Wallet:
    def __init__(self):

    def new_wallet(self):
        random_generator = Random.new().read
        key = RSA.generate(1024, random_generator)

        private_key = key.exportKey(format='DER')
        public_key = key.publickey().exportKey(format='DER')

        response = {
            'private_key': hexlify(private_key).decode('ascii'),
            'address': hexlify(public_key).decode('ascii'),
        }
        
        return response