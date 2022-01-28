import hashlib
import json
from time import time
from uuid import uuid4
from urllib.parse import urlparse
import datetime

from flask import Flask, jsonify, request,render_template


class BlockChain(object):
    """ Main BlockChain class """
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        # create the genesis block
        self.new_block(previous_hash=1, proof=100)

    @staticmethod
    def hash(block):
        # hashes a block
        # also make sure that the transactions are ordered otherwise we will have insonsistent hashes!
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def new_block(self, proof, previous_hash=None):
        # creates a new block in the blockchain
        block = {
            'index': len(self.chain)+1,
            'timestamp': str(datetime.datetime.now()),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # reset the current list of transactions
        self.current_transactions = []
        self.chain.append(block)
        return block

    @property
    def last_block(self):
        # returns last block in the chain
        return self.chain[-1]

    def new_transaction(self, sender, recipient, amount):
        # adds a new transaction into the list of transactions
        # these transactions go into the next mined block

        self.current_transactions.append({
            "sender":sender,
            "recipient":recipient,
            "amount":amount,
        })
        if len(self.current_transactions)>1:
            self.current_transactions.pop(1)

        return int(self.last_block['index'])+1

    def proof_of_work(self, last_proof):
        # simple proof of work algorithm
        # find a number p' such as hash(pp') containing leading 4 zeros where p is the previous p'
        # p is the previous proof and p' is the new proof
        proof = 0
        while self.validate_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def validate_proof(last_proof, proof):
        # validates the proof: does hash(last_proof, proof) contain 4 leading zeroes?
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def register_node(self, address):
        # add a new node to the list of nodes
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def full_chain(self):
        # xxx returns the full chain and a number of blocks
        pass


# initiate the node
app = Flask(__name__)
# generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')
# initiate the Blockchain
blockchain = BlockChain()

@app.route('/mine', methods=['GET'])
def mine():

    # first we need to run the proof of work algorithm to calculate the new proof..
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # we must recieve reward for finding the proof in form of receiving 1 Coin
    blockchain.new_transaction(
        sender=None,
        recipient=None,
        amount=0,
    )

    # forge the new block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "Forged new block.",
        'index': block['index'],
        'timestamp': block['timestamp'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }

    aaa = blockchain.chain
    # return jsonify(response, 200)
    return render_template('index.html',a= {'topo':response,'chaindata':aaa})


@app.route('/transaction/new', methods=['POST'])
def new_transaction():
    sender = request.form.get('sender')
    recipient = request.form.get('recpient')
    amount = request.form.get('amount')
    timestamp = request.form.get('timestamp')
    print(sender,recipient,amount,timestamp,'bfgvhfjdh')


    # create a new transaction
    index = blockchain.new_transaction(
        sender = sender,
        recipient = recipient,
        amount = amount
    )

    response = {
        'message': f'Transaction will be added to the Block {index}',
    }
    # return jsonify(response, 200)
    return render_template('index.html', msg=response)

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    aaa = blockchain.chain
    # return jsonify(response), 200
    return render_template('index.html', chaindata=aaa)


@app.route('/')
def index():
    aaa = blockchain.chain
    # return jsonify(response, 200)
    return render_template('index.html', a={'chaindata': aaa})



