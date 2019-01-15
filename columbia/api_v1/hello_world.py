import time

from columbia.tasks.hello_world import hello_world


def get():
    return {'hello_world': True}, 200


def remote():
    result = hello_world.delay()
    while not result.ready():
        time.sleep(0.5)
    return result.get()
