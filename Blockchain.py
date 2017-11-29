#Responsible for managing the chain
#Stores transactions, can add new blocks to chain
# Each Block will contain an index, a timestamp, list of transactions, a proof, and a hash of prev Block
import hashlib
import json
from uuid import uuid4
from time import time

from flask import Flask



class Blockchain(object):

    #Flask
    #Instantiate our Node
    app = Flask(__name__)

    #Generate globally unique address for node
    node_identifier = str(uuid4()).replace('-','')

    #Instantiate Blockchain
    blockchain = Blockchain()

    @app.route('/mine', methods=['GET'])
    def mine():
        return "We'll mine a new Block"

    @app.route('/transactions/new', methods=['POST'])
    def new_transaction():
        values = request.get_json()

        #Check req fields are in POST area
        required = ['sender', 'recipient', 'amount']
        if not all(k in values for k in required):
            return 'Missing values', 400

        #Create new transaction
        index = blockchain.new_transaction(values['sender'],values['recipient'],values['amount'])
        response = {'message': f'Transaction will be added to block {index}'}
        return jsonify(response), 201

    @app.route('/chain', methods=['GET'])
    def full_chain():
        response = {
            'chain': blockchain.chain,
            'length': len(blockchain.chain),
        }
        return jsonify(response), 200

    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5000)

    def __init__(self):
        self.chain = []
        self.current_transactions = []

        #genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        #Creating new block and adding it to the chain
        """
                Create a new Block in the Blockchain
                :param proof: <int> The proof given by the Proof of Work algorithm
                :param previous_hash: (Optional) <str> Hash of previous Block
                :return: <dict> New Block
                """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        #Reset curr list of transactions
        self.current_transactions = []

        self.chain.append(block)

        return block


    def new_transaction(self, sender, recipient, amount):
        """
                Creates a new transaction to go into the next mined Block
                :param sender: <str> Address of the Sender
                :param recipient: <str> Address of the Recipient
                :param amount: <int> Amount
                :return: <int> The index of the Block that will hold this transaction
                """
        #Add new transaction to transaction list
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block['index'] + 1

       # After new_transaction() adds a transaction to the list, it returns the index of the block which the
        # transaction will be added to—the next one to be mined. This will be useful later on, to the user submitting
        #  the transaction.

    def proof_of_work(self, last_proof):
        # Simple Proof of Work Alg:
        # -Find number 'p' such that hash(pp') contains leading zeros where the p is the previous p'
        # - p is previous proof, p' is new proof

        proof = 0
        while (self.valid_proof(last_proof, proof)) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        #Validates proof: does hash contain 4 leading zeros?
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def hash(block):
        #Creates SHA-256 Hash of Block
        # param block: <dict> Block
        # return <str>
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        #returns last block in chain
        return self.chain[-1]


