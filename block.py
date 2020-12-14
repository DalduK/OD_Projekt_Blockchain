from hashlib import sha256
import json
import time

class Block:
    def __init__(self, index, transaction, timestamp, previous_hash):
        # Unikalny ID bloku
        self.index = index
        # Lista transakcji
        self.transaction = transaction
        # Dokładny czas w którym blok został wygenerowany
        self.timestamp = timestamp
        # Hash poprzedniego bloku w łańcuchu bloków
        self.previous_hash = previous_hash

    def compute_hash(self):
        # Zwraca hash bloku który reprezentowany jest jako JSON string
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()

class Blockchain:
    # trudność w obliczeniu algorytmu Proof of work
    difficulty = 2

    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def proof_of_work(self, block):
        block.nonce = 0

        compute_hash = block.compute_hash()
        while not compute_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return  computed_hash

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

    def is_valid_proof(self, block, block_hash):
        # funkcja sprawdza czy dany blok spełnia wszystkie kryteria
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    def create_genesis_block(self):
        # funkcja która tworzy blok początkowy (genesis) i dodaje go do łacucha bloków,
        # Blok posiada indeks 0, a hash poprzedniego bloku również ustawionu jest jako 0
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]