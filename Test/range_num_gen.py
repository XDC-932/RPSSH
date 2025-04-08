import random

def gen():
    var = random.randint(0, 2000)
    var = (float(var) - 1000) / 1000
    return var

def gen_list(n):
    queue = []
    for i in range(n):
        queue.append(gen())
    return queue