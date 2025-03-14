import redis
import time
import psutil
import string
import random
import os

def RandomString(length):
    chars = string.ascii_letters + string.digits
    return ''.join([random.choice(chars) for i in range(length)])

def Measure():
    return psutil.cpu_percent(), psutil.cpu_freq().current, RandomString(5)

def Mainloop(host, port, db):
    rd = redis.Redis(host=host, port=port, db=db)
    interval = 1
    data_key = 'cpu'
    data_columns = 'CPU Percent,CPU Frequency,Random String'
    rd.set('data_key', data_key)
    rd.set('data_columns', data_columns)
    keep_period = 60 * 60 * 24
    remove_interval = 600
    prev = time.perf_counter()
    prev_remove = time.perf_counter()
    while True:
        now = time.perf_counter()
        if now - prev >= interval:
            ret = str(Measure())
            score = int(time.time() * 1000)
            value = {
                ret: score
            }
            rd.zadd(data_key, value)
            prev = now
        if now - prev_remove >= remove_interval:
            limit = int((time.time() - keep_period) * 1000)
            rd.zremrangebyscore(data_key, float('-inf'), limit)
            prev_remove = now

if __name__ == '__main__':
    host = os.environ.get('REDIS_HOST', '127.0.0.1')
    port = os.environ.get('REDIS_PORT', 6379)
    db = os.environ.get('REDIS_DB', 1)
    Mainloop(host, port, db)

