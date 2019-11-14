import random
import sys

from app.block import Block


class Session():
    
    def __init__(self, categories, session_length, number_of_categories):
        self.categories = categories
        self.session_length = session_length
        self.number_of_categories = number_of_categories
        self.blocks = self.generate_blocks()

    def generate_blocks(self):
        blocks = set([])
        categories_set = self.create_categories_set()
        minutes_per_category = self.session_length / self.number_of_categories
        for category in categories_set:
            block = Block(minutes_per_category, category)
            blocks.add(block)
        print(f'{blocks}', file=sys.stderr)
        return blocks

    def create_categories_set(self):
        categories_set = set([])
        while len(categories_set) < self.number_of_categories:
            categories_set.add(random.choice(self.categories))
        return categories_set

    def __repr__(self):
        return f'<Session: categories={self.categories}, session_length={self.session_length,}>, number_of_categories={self.number_of_categories}, blocks={self.blocks}'
