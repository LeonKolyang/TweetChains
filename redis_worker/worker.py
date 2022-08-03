import os
from urllib.parse import urlparse, uses_netloc
from redis import Redis
from rq import Queue, Connection


listen = ['high', 'default', 'low']

redis_url = os.getenv('REDIS_URL', "redis://localhost:6379")
if not redis_url:
    raise RuntimeError('Set up Redis To Go first.')
elif "localhost" in redis_url:
    from rq.worker import Worker #HerokuWorker as Worker
else:
    from rq.worker import HerokuWorker as Worker

uses_netloc.append('redis')
url = urlparse(redis_url)
conn = Redis(host=url.hostname, port=url.port, db=0, password=url.password)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()