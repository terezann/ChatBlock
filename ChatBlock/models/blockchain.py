class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        # Create the first block (genesis block)
        # Customize as per your requirements
        genesis_block = Block(0, "1", "Genesis Block", "genesis_hash")
        return genesis_block

    def create_new_block(self, data):
        # Create a new block and add it to the chain
        previous_block = self.chain[-1]
        new_index = previous_block.index + 1
        new_timestamp = time.time()
        new_hash = self.calculate_hash(new_index, previous_block.hash, new_timestamp, data)
        new_block = Block(new_index, previous_block.hash, new_timestamp, data, new_hash)
        return new_block