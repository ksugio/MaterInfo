import redis
import time
import signal
import psutil
import string
import random
import os

def RandomString(length):
    chars = string.ascii_letters + string.digits
    return ''.join([random.choice(chars) for i in range(length)])

def Measure():
    return psutil.cpu_percent(), psutil.cpu_freq().current, RandomString(5)

# start program
host = os.environ.get('REDIS_HOST', '127.0.0.1')
port = os.environ.get('REDIS_PORT', 6379)
db = os.environ.get('REDIS_DB', 1)
rd = redis.Redis(host=host, port=port, db=db)
interval = 1
data_key = 'cpu'
data_columns = 'CPU Percent,CPU Frequency,Random String'
rd.set('data_key', data_key)
rd.set('data_columns', data_columns)

def handler(signum, frame):
    ret = str(Measure())
    now = time.time()
    value = {
        ret: int(now * 1000)
    }
    rd.zadd(data_key, value)

signal.signal(signal.SIGALRM, handler)
signal.setitimer(signal.ITIMER_REAL, interval, interval)

keep_period = 60 * 60 * 24
remove_interval = 600
while True:
    time.sleep(remove_interval)
    limit = int((time.time() - keep_period) * 1000)
    rd.zremrangebyscore(data_key, float('-inf'), limit)
