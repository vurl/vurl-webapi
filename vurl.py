import os

import redis
from hashids import Hashids
from yhttp import Application, text, statuses, validate, statuscode


__version__ = '0.2.0'


hashids = Hashids()


app = Application()
redis = redis.Redis()


def getfreshid():
    randomint = int.from_bytes(os.urandom(6), 'big')
    return hashids.encode(randomint)


def store(url):
    while True:
        freshid = getfreshid()
        if redis.setnx(freshid, url):
            break

    return freshid


@app.route('/(.*)')
def get(req, key):
    longurl = redis.get(key)
    if not longurl:
        raise statuses.notfound()

    raise statuses.found(longurl.decode())


@app.route()
@validate(fields=dict(url=dict(
    required='400 Field missing: url',
    pattern=(r'^https?://.*', '400 Invalid URL')
)))
@text
@statuscode('201 Created')
def post(req):
    return store(req.form['url'])

