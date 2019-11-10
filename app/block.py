import random

from app.task import Task

class Block():

    def __init__(self, len_in_min, category):
        self.len_in_min = len_in_min
        self.category = category
        self.task = self.get_task()

    def get_task(self):
        return random.choice(self.category.tasks)

    def __repr__(self):
        return f'<Block: len_in_min={self.len_in_min}, category={self.category,}>, task={self.task}'
