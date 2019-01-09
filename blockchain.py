import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transaction = []

        # Create the genesis block
        self.new_block(previous_hash='1', proof=100)
        print(self.chain)

    def new_block(self, previous_hash, proof):
        """Create a new Block in the Blockchain

        Args:
            proof (int): The proof given by the Proof of Work algorithm
            previous_hash (Optional) (str): Hash of previous Block

        Returns:
            dict: New Block
        """

        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.chain[-1])
        }

        # Reset the current list of transaction
        self.current_transaction = []
        self.chain.append(block)

        return block

    def new_transaction(self, sender, recipient, amount):
        """Creates a new Block and adds it to the chain

        Args:
            sender (str): Address of the Sender
            recipient (str): Address of the Recipient
            amount (int): Amount
        Returns:
            int: The index of the Block that will hold this transaction

        """

        self.current_transaction.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })
        return self.last_block['index'] + 1

    def proof_of_work(self, last_block):
        """
        Simple Proof of Work Algorithm:
            - Find a number p' such that hash(pp') contains leading 4 zeros, where p is the previous p'
            - p is the previous proof, and p' is the new proof

        Args:
            last_block (int): last block

        Returns:
            int: new proof

        """
        last_proof = last_block['proof']
        last_hash = self.hash(last_block)
        proof = 0
        while self.valid_proof(last_proof, last_hash) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """Validates the Proof: Does hash(last_proof, proof) contains 4 leading zeros?

        Args:
            last_proof (int): last_proof
            proof (int): proof

        Returns:
            bool: Does hash(last_proof, proof) contains 4 leading zeros(True) or not(False).

        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """Creates a SHA-256 hash of a Block

        Args:
            block (dict): Block

        Returns:
            str: Hash of Block

        """

        # We must make sure thar the Dictionary is Ordered, or we'll have inconsistent hashes.
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


# instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    # last_block = Blockchain.last_block
    last_block = blockchain.chain[-1]
    proof = blockchain.proof_of_work(last_block)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(previous_hash, proof)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transaction': block['transaction'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }
    return jsonify(response), 200


@app.route('/transactions/new')
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data

    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}

    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
