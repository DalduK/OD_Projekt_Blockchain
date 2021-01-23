from flask import Flask, request
from hashlib import sha256
import json
import time
import requests

app = Flask(__name__)



class Block:
    def __init__(self, index, transaction, timestamp, previous_hash, nonce=0):
        # Unikalny ID bloku
        self.index = index
        # Lista transakcji
        self.transaction = transaction
        # Dokładny czas w którym blok został wygenerowany
        self.timestamp = timestamp
        # Hash poprzedniego bloku w łańcuchu bloków
        self.previous_hash = previous_hash
        self.nonce = nonce

    def compute_hash(self):
        # Zwraca hash bloku który reprezentowany jest jako JSON string
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()

class Blockchain:
    # trudność w obliczeniu algorytmu Proof of work
    difficulty = 1

    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []

    def create_genesis_block(self):
        # funkcja która tworzy blok początkowy (genesis) i dodaje go do łacucha bloków,
        # Blok posiada indeks 0, a hash poprzedniego bloku również ustawionu jest jako 0
        genesis_block = Block(0, [], 0, "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def proof_of_work(block):
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash

    def add_block(self, block, proof):
        # funkcja która dodaje blok do łańcucha po weryfikacji czy PoW jest poprawny,
        # również czy ostatni hash bloku jest równy temu podanemu w bloku
        previous_hash = self.last_block.hash
        if previous_hash != block.previous_hash:
            return False

        if not Blockchain.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    @classmethod
    def is_valid_proof(cls, block, block_hash):
        # funkcja sprawdza czy dany blok spełnia wszystkie kryteria
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    def mine(self):
        # funkcja pozwala na dodanie oczekujących transakcji do blockchainu, poprzez dodanie do bloku i rozwiązanie PoW
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block

        new_block = Block(index=last_block.index + 1,
                          transaction=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []
        return True

    @classmethod
    def check_chain_validity(cls, chain):
        result = True
        previous_hash = "0"
        for block in chain:
            block_hash = block.hash
            delattr(block, "hash")
            if not cls.is_valid_proof(block, block.hash) or \
                    previous_hash != block.previous_hash:
                result = False
                break
            block.hash, previous_hash = block_hash, block_hash

        return result


blockchain = Blockchain()
blockchain.create_genesis_block()

peers = set()

# TODO Broadcasting peers
@app.route('/register_node', methods=['POST'])
def register_new_peers():
    node_address = request.get_json()["node_address"]
    for i in node_address:
        if not i:
            return "Invalid data", 400
        if i != request.host_url:
            peers.add(i)
    dict_peers = {}
    dict_peers["node_addresses"] = list(peers)
    announce_new_peers(dict_peers)
    return get_chain()


@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    node_address = request.get_json()["node_address"]
    global peers
    if not node_address:
        return "Invalid data", 400
    temp = []
    for i in peers:
        temp.append(i)
    temp.append(request.host_url)
    data = {"node_address": temp}
    headers = {'Content-Type': "application/json"}

    response = requests.post(node_address + "/register_node",
                             data=json.dumps(data), headers=headers)
    if response.status_code == 200:
        global blockchain

        #aktualizacja łańcucha i peerów
        chain_dump = response.json()['chain']
        prob_peers = response.json()['peers']
        blockchain = create_chain_from_dump(chain_dump)
        chain = {}
        chain["chain"] = chain_dump
        for i in peers:
            requests.post(i + "/chain_dump",
                                     data=json.dumps(chain), headers=headers)
        print(response.json()['peers'])
        peers.add(node_address+"/")
        for i in prob_peers:
            if i != request.host_url:
                peers.add(i)
        dict_peers = {}
        dict_peers["node_addresses"] = list(peers)
        announce_new_peers(dict_peers)
        return "Registration succesful", 200
    else:
        return response.content, response.status_code

# @app.route('/register_node', methods=['POST'])
# def register_new_peers():
#     node_address = request.get_json()["node_address"]
#     sender = request.get_json()["sender"]
#     ttl = int(request.get_json()["ttl"]) - 1
#     if not node_address:
#         return "Invalid data", 400
#     print('ADRESSS ', node_address)
#     if node_address != request.host_url:
#         peers.add(node_address)
#     if sender != request.host_url:
#         peers.add(sender)
#
#     if ttl > 0:
#         data = {"node_address": node_address,
#                 "sender": request.host_url,
#                 "ttl": ttl}
#         headers = {'Content-Type': "application/json"}
#
#         for peer in peers.copy():
#             print(ttl)
#             print(data)
#             response = requests.post(peer + "/register_node",
#                                      data=json.dumps(data), headers=headers)
#             print(response)
#
#     return get_chain()
#
#
# @app.route('/register_with', methods=['POST'])
# def register_with_existing_node():
#     node_address = request.get_json()["node_address"]
#     if not node_address:
#         return "Invalid data", 400
#     # print(type(node_address))
#     data = {"node_address": request.host_url,
#             "sender": request.host_url,
#             "ttl": 3}
#     headers = {'Content-Type': "application/json"}
#
#     response = requests.post(node_address + "/register_node",
#                              data=json.dumps(data), headers=headers)
#     if response.status_code == 200:
#         global blockchain
#         global peers
#         chain_dump = response.json()['chain']
#         blockchain = create_chain_from_dump(chain_dump)
#         print(response.json()['peers'])
#         peers.add(node_address+"/")
#         return "Registration succesful", 200
#     else:
#         return response.content, response.status_code

@app.route('/chain_dump', methods=['POST'])
def send_chain_to_peers():
    global blockchain
    chain = request.get_json()["chain"]
    blockchain = create_chain_from_dump(chain)
    return "Success", 200

@app.route('/announce_peers', methods=['POST'])
def send_added_peers():
    node_address = request.get_json()["node_addresses"]
    for i in node_address:
        for j in peers.copy():
            if i != j and i != request.host_url:
                peers.add(i)
            else:
                continue
    return "Registration succesful", 200

@app.route('/announce_leave', methods=['POST'])
def send_leave():
    node_add = request.get_json()["node_address"]
    print(node_add)
    print(peers)
    if not node_add:
        return "invalid data", 400
    peers.remove(node_add)
    return "success", 200

@app.route('/leave', methods=['GET'])
def get_leave():
    for i in peers.copy():
        url = "{}announce_leave".format(i)
        headers = {'Content-Type': "application/json"}
        dict = {"node_address": request.host_url}
        requests.post(url, data=json.dumps(dict, sort_keys=True), headers=headers)
        peers.remove(i)

    return "Success", 200

def create_chain_from_dump(chain_dump):
    generated_blockchain = Blockchain()
    generated_blockchain.create_genesis_block()
    for idx, block_data in enumerate(chain_dump):
        if idx == 0:
            continue
        block = Block(block_data["index"],
                      block_data["transaction"],
                      block_data["timestamp"],
                      block_data["previous_hash"],
                      block_data["nonce"])
        proof = block_data['hash']
        added = generated_blockchain.add_block(block, proof)
        if not added:
            raise Exception("The chain dump is tampered!!")
    return generated_blockchain
# ###################################

@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    required_fields = ["ID", "Money", "Description"]

    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data", 404

    tx_data["timestamp"] = time.time()

    blockchain.add_new_transaction(tx_data)
    announce_new_block_to_mine(tx_data)

    return "Success", 201

@app.route('/share_transaction', methods=['POST'])
def share_transaction():
    tx_data = request.get_json()
    required_fields = ["ID", "Money", "Description", "timestamp"]

    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data", 404

    blockchain.add_new_transaction(tx_data)

    return "Success", 201

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data), "chain": chain_data, "peers": list(peers)})

@app.route('/miner', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    else:
        chain_length = len(blockchain.chain)
        consensus()
        if chain_length == len(blockchain.chain):
            announce_new_block(blockchain.last_block)
        return "Block #{} is mined.".format(blockchain.last_block.index)

@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)

@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()
    block = Block(block_data["index"],
                  block_data["transaction"],
                  block_data["timestamp"],
                  block_data["previous_hash"],
                  block_data["nonce"])
    dict = block_data["transaction"]
    for d in dict:
        for i in blockchain.unconfirmed_transactions:
            if d["timestamp"] == i["timestamp"]:
                blockchain.unconfirmed_transactions.remove(i)
    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return "The Block was discarded by the node", 400

    return "Block added to the chain", 201

def announce_new_block(block):
    for peer in peers:
        url = "{}add_block".format(peer)
        headers= {'Content-Type': "application/json"}
        requests.post(url, data=json.dumps(block.__dict__, sort_keys=True), headers=headers)

def announce_new_block_to_mine(tx_data):
    for peer in peers:
        url = "{}share_transaction".format(peer)
        headers= {'Content-Type': "application/json"}
        requests.post(url, data=json.dumps(tx_data, sort_keys=True), headers=headers)

def announce_new_peers(tx_data):
    for peer in peers:
        url = "{}announce_peers".format(peer)
        headers= {'Content-Type': "application/json"}
        requests.post(url, data=json.dumps(tx_data, sort_keys=True), headers=headers)

def send_own_peers(tx_data, peer):
    url = "{}announce_peers".format(peer)
    headers= {'Content-Type': "application/json"}
    requests.post(url, data=json.dumps(tx_data, sort_keys=True), headers=headers)

def consensus():
    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:
        response = requests.get('{}chain'.format(node))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True

    return False

if __name__ == "__main__":
    app.run(threaded=True, port=8001)