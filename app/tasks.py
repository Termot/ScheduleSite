import time
from app import make_celery

celery = make_celery()

@celery.Task()
def example(seconds):
    print('Starting task')
    for i in range(seconds):
        print(i)
        time.sleep(1)
    print('Task completed')
