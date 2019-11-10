import random
import sys
#from flask import flash

TASKS_BY_CATEGORY = {
    'Acoustic': ['Find fingerstyle blues to play'], 
    'Electric': ['Frankenstein by Edgar Winter Group'], 
    'Guitar Gods': ['Have A Cigar by Pink Floyd'], 
    'Improvisation': ['Find some 2-chord vamp ideas to jam'],
    'Fingerstyle': ['Come and Find Me by Josh Ritter'], 
    'Slide': ['Find slide course to work through'], 
    'Pyrotechnics': ['Find more tapping licks'], 
    'Songwriting': ['Compile Session'],
    'Open Mic': ['Motion Pictures'], 
    'Band Performance': ['Practice Bridge People solos'], 
    'Technical Mastery': ['Organize technique exercises'], 
    'Music Theory': ['Ch.1 in theory book']
}

class Task():

    def __init__(self, title):
        self.title = title

    @staticmethod
    def get_category_task(category):
        print(TASKS_BY_CATEGORY, file=sys.stderr)
        tasks_by_category = TASKS_BY_CATEGORY.get(category, "default")
        print(tasks_by_category, file=sys.stderr)
        print('Hello world!', file=sys.stderr)
        task = random.choice(tasks_by_category)
        return Task(task)